import logging
from functools import lru_cache
from uuid import uuid4
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import STATIC_DIR, get_settings
from app.gemini_service import GeminiService, GeminiServiceError
from app.validators import read_and_validate_image, validate_question


logger = logging.getLogger("wizyvision.requests")
TRACKED_PATHS = {"/ask", "/ask-agentic"}


class HealthResponse(BaseModel):
    status: str


class AskResponse(BaseModel):
    answer: str
    model: str | None
    request_id: str


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
    request_id: str


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


def generate_request_id() -> str:
    return f"req_{uuid4().hex[:8]}"


def _get_request_mode_and_model(path: str) -> tuple[str | None, str | None]:
    if path == "/ask":
        return "normal", settings.model_name

    if path == "/ask-agentic":
        return "agentic", settings.agentic_model_name

    return None, None


@app.middleware("http")
async def attach_request_id_and_log(request: Request, call_next):
    mode, model = _get_request_mode_and_model(request.url.path)
    request_id = generate_request_id() if mode else None
    request.state.request_id = request_id

    response = await call_next(request)

    if request_id:
        success = response.status_code < 400
        logger.info(
            "request_id=%s endpoint=%s mode=%s model=%s success=%s status_code=%s",
            request_id,
            request.url.path,
            mode,
            model,
            success,
            response.status_code,
        )

    return response


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "The request was rejected."
    payload = {"detail": detail}
    request_id = getattr(request.state, "request_id", None)

    if request_id:
        payload["request_id"] = request_id

    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    _ = exc
    payload = {"detail": "The request was rejected. Please check the submitted fields."}
    request_id = getattr(request.state, "request_id", None)

    if request_id:
        payload["request_id"] = request_id

    return JSONResponse(status_code=422, content=payload)


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "request_id=%s endpoint=%s unexpected_error=%s",
        getattr(request.state, "request_id", None),
        request.url.path,
        exc.__class__.__name__,
    )

    payload = {"detail": "The server could not process the request. Please try again."}
    request_id = getattr(request.state, "request_id", None)

    if request_id:
        payload["request_id"] = request_id

    return JSONResponse(status_code=500, content=payload)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
async def ask_image_question(
    request: Request,
    image: Annotated[UploadFile | None, File()] = None,
    question: Annotated[str | None, Form()] = None,
) -> AskResponse:
    result = await _handle_question_request(
        image=image,
        question=question,
        agentic=False,
    )
    return AskResponse(
        answer=result["answer"],
        model=result["model"],
        request_id=request.state.request_id,
    )


@app.post("/ask-agentic", response_model=AskAgenticResponse)
async def ask_image_question_agentic(
    request: Request,
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
        request_id=request.state.request_id,
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
