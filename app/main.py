from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import STATIC_DIR, Settings, get_settings
from app.gemini_service import GeminiService
from app.validators import read_and_validate_image, validate_question


class HealthResponse(BaseModel):
    status: str


class AskResponse(BaseModel):
    answer: str
    model: str | None


@lru_cache
def get_gemini_service() -> GeminiService:
    settings = get_settings()
    return GeminiService(
        api_key=settings.gemini_api_key,
        timeout_seconds=settings.request_timeout_seconds,
    )


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
async def ask_image_question(
    image: Annotated[UploadFile, File(...)],
    question: Annotated[str, Form(...)],
) -> AskResponse:
    settings = get_settings()
    gemini_service = get_gemini_service()
    cleaned_question = validate_question(question)

    try:
        image_bytes = await read_and_validate_image(
            image=image,
            max_upload_size_bytes=settings.max_upload_size_bytes,
        )
        result = await gemini_service.answer_question_about_image(
            image_bytes=image_bytes,
            image_content_type=image.content_type or "application/octet-stream",
            question=cleaned_question,
        )
    except HTTPException:
        raise
    finally:
        await image.close()

    return AskResponse(answer=result["answer"], model=result["model"])
