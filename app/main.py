from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import STATIC_DIR, get_settings
from app.gemini_service import GeminiService, GeminiServiceError
from app.validators import read_and_validate_image, validate_question


class HealthResponse(BaseModel):
    status: str


class AskResponse(BaseModel):
    answer: str
    model: str | None


class AgenticTimelineItem(BaseModel):
    type: str
    content: str | None = None
    language: str | None = None
    code: str | None = None
    output: str | None = None
    outcome: str | None = None
    mime_type: str | None = None
    data: str | None = None


class AskAgenticResponse(BaseModel):
    answer: str
    model: str
    mode: str
    timeline: list[AgenticTimelineItem]


@lru_cache
def get_gemini_service() -> GeminiService:
    settings = get_settings()
    return GeminiService(
        api_key=settings.gemini_api_key,
        model_name=settings.model_name,
        agentic_model_name=settings.agentic_model_name,
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
    image: Annotated[UploadFile | None, File()] = None,
    question: Annotated[str | None, Form()] = None,
) -> AskResponse:
    result = await _handle_question_request(
        image=image,
        question=question,
        agentic=False,
    )
    return AskResponse(answer=result["answer"], model=result["model"])


@app.post("/ask-agentic", response_model=AskAgenticResponse)
async def ask_image_question_agentic(
    image: Annotated[UploadFile | None, File()] = None,
    question: Annotated[str | None, Form()] = None,
) -> AskAgenticResponse:
    result = await _handle_question_request(
        image=image,
        question=question,
        agentic=True,
    )
    return AskAgenticResponse(
        answer=result["answer"],
        model=result["model"],
        mode=result["mode"],
        timeline=[
            AgenticTimelineItem(**timeline_item) for timeline_item in result["timeline"]
        ],
    )


async def _handle_question_request(
    *,
    image: UploadFile | None,
    question: str | None,
    agentic: bool,
) -> dict:
    settings = get_settings()
    gemini_service = get_gemini_service()
    cleaned_question = validate_question(question)

    try:
        image_bytes = await read_and_validate_image(
            image=image,
            max_upload_size_bytes=settings.max_upload_size_bytes,
        )
        if agentic:
            result = await gemini_service.answer_question_about_image_agentic(
                image_bytes=image_bytes,
                image_content_type=image.content_type or "application/octet-stream",
                question=cleaned_question,
            )
        else:
            result = await gemini_service.answer_question_about_image(
                image_bytes=image_bytes,
                image_content_type=image.content_type or "application/octet-stream",
                question=cleaned_question,
            )
    except HTTPException:
        raise
    except GeminiServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    finally:
        if image is not None:
            await image.close()

    return result
