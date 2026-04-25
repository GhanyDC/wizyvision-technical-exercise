class GeminiService:
    def __init__(self, *, api_key: str | None, timeout_seconds: float) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    async def answer_question_about_image(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict[str, str | None]:
        _ = image_bytes, image_content_type, question, self._api_key, self._timeout_seconds

        # TODO: Replace this stub with a real Gemini API call.
        # Keep the API key server-side and return the actual model name used.
        return {
            "answer": "Gemini integration not implemented yet.",
            "model": None,
        }
