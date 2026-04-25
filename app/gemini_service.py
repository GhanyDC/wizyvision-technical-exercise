import base64
from http import HTTPStatus
from typing import Any

from google import genai
from google.genai import errors, types


STANDARD_SYSTEM_INSTRUCTION = (
    "You are an image analysis assistant for field operations. "
    "Answer the user's question as precisely and directly as possible using "
    "only visible evidence from the image. Do not guess if the information "
    "is unclear or unreadable. If the answer is uncertain, briefly explain "
    "what is not visible or not legible. Prefer concise, actionable answers "
    "over general descriptions."
)

AGENTIC_SYSTEM_INSTRUCTION = (
    "You are an image analysis assistant for field operations. "
    "Answer the user's question as precisely and directly as possible using "
    "only visible evidence from the image. When useful, use Python code "
    "execution to inspect, zoom, crop, count, or annotate the image. "
    "Do not guess if information is unclear or unreadable. If the answer "
    "is uncertain, briefly explain what is not visible or not legible. "
    "Prefer concise, actionable answers over general descriptions."
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
        agentic_model_name: str,
        timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._agentic_model_name = agentic_model_name
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

        config = types.GenerateContentConfig(
            system_instruction=STANDARD_SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=256,
        )

        try:
            response = await self._generate_content(
                model_name=self._model_name,
                question=question,
                image_bytes=image_bytes,
                image_content_type=image_content_type,
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

    async def answer_question_about_image_agentic(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict[str, Any]:
        if not self._api_key:
            raise GeminiServiceError(
                "Gemini is not configured on the server.",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            )

        config = types.GenerateContentConfig(
            system_instruction=AGENTIC_SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=512,
            tools=[types.Tool(code_execution=types.ToolCodeExecution())],
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=-1,
            ),
        )

        try:
            response = await self._generate_content(
                model_name=self._agentic_model_name,
                question=question,
                image_bytes=image_bytes,
                image_content_type=image_content_type,
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

        return self._parse_agentic_response(response)

    async def _generate_content(
        self,
        *,
        model_name: str,
        question: str,
        image_bytes: bytes,
        image_content_type: str,
        config: types.GenerateContentConfig,
    ) -> types.GenerateContentResponse:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_content_type,
        )

        async with genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(timeout=self._timeout_ms),
        ).aio as client:
            return await client.models.generate_content(
                model=model_name,
                contents=[image_part, question],
                config=config,
            )

    def _parse_agentic_response(
        self,
        response: types.GenerateContentResponse,
    ) -> dict[str, Any]:
        candidates = response.candidates or []
        if not candidates or candidates[0].content is None:
            raise GeminiServiceError(
                "Gemini did not return a usable answer. Please try again."
            )

        timeline: list[dict[str, Any]] = []
        answer_candidates: list[str] = []

        for part in candidates[0].content.parts or []:
            if part.text and part.text.strip():
                text = part.text.strip()
                if part.thought:
                    timeline.append(
                        {
                            "type": "think",
                            "content": text,
                        }
                    )
                else:
                    answer_candidates.append(text)

            if part.executable_code and part.executable_code.code:
                timeline.append(
                    {
                        "type": "act",
                        "language": self._normalize_language(part.executable_code.language),
                        "code": part.executable_code.code.strip(),
                    }
                )

            if part.code_execution_result:
                output = (part.code_execution_result.output or "").strip()
                outcome = self._normalize_outcome(part.code_execution_result.outcome)
                if not output:
                    output = outcome.replace("_", " ").title() if outcome else "No output."

                timeline.append(
                    {
                        "type": "observe",
                        "output": output,
                        "outcome": outcome,
                    }
                )

            if part.inline_data and self._is_image_blob(part.inline_data):
                timeline.append(
                    {
                        "type": "image",
                        "mime_type": part.inline_data.mime_type,
                        "data": base64.b64encode(part.inline_data.data).decode("ascii"),
                    }
                )

        final_answer = answer_candidates[-1] if answer_candidates else ""
        if not final_answer:
            raise GeminiServiceError(
                "Gemini did not return a usable answer. Please try again."
            )

        return {
            "answer": final_answer,
            "model": self._agentic_model_name,
            "mode": "agentic",
            "timeline": timeline,
        }

    def _is_image_blob(self, blob: types.Blob) -> bool:
        return bool(blob.data and blob.mime_type and blob.mime_type.startswith("image/"))

    def _normalize_language(self, language: types.Language | None) -> str:
        if language is None:
            return "python"

        return language.value.lower().replace("language_", "")

    def _normalize_outcome(self, outcome: types.Outcome | None) -> str | None:
        if outcome is None:
            return None

        return outcome.value.lower()

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
