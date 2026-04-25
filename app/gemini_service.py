from http import HTTPStatus

from google import genai
from google.genai import errors, types


SYSTEM_INSTRUCTION = (
    "You are an image analysis assistant for field operations. "
    "Answer the user's question as precisely and directly as possible using "
    "only visible evidence from the image. Do not guess if the information "
    "is unclear or unreadable. If the answer is uncertain, briefly explain "
    "what is not visible or not legible. Prefer concise, actionable answers "
    "over general descriptions."
)


class GeminiServiceError(Exception):
    def __init__(self, message: str, status_code: int = HTTPStatus.BAD_GATEWAY) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GeminiService:
    def __init__(
        self,
        *,
        api_key: str | None,
        model_name: str,
        timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._timeout_ms = int(timeout_seconds * 1000)

    async def answer_question_about_image(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict[str, str]:
        if not self._api_key:
            raise GeminiServiceError(
                "Gemini is not configured on the server.",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            )

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_content_type,
        )
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=256,
        )

        try:
            async with genai.Client(
                api_key=self._api_key,
                http_options=types.HttpOptions(timeout=self._timeout_ms),
            ).aio as client:
                response = await client.models.generate_content(
                    model=self._model_name,
                    contents=[question, image_part],
                    config=config,
                )
        except errors.ClientError as exc:
            raise self._translate_client_error(exc) from exc
        except errors.ServerError as exc:
            raise GeminiServiceError(
                "Gemini is temporarily unavailable. Please try again.",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        except Exception as exc:
            raise GeminiServiceError("Gemini request failed. Please try again.") from exc

        answer = (response.text or "").strip()
        if not answer:
            raise GeminiServiceError(
                "Gemini did not return a usable answer. Please try again."
            )

        return {
            "answer": answer,
            "model": self._model_name,
        }

    def _translate_client_error(self, exc: errors.ClientError) -> GeminiServiceError:
        if exc.code in {401, 403}:
            return GeminiServiceError(
                "Gemini is not configured on the server.",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            )

        if exc.code == 429:
            return GeminiServiceError(
                "Gemini is temporarily busy. Please try again.",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            )

        if exc.code in {400, 404, 413, 415, 422}:
            return GeminiServiceError("Gemini could not process this image and question.")

        return GeminiServiceError("Gemini request failed. Please try again.")
