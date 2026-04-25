from fastapi.testclient import TestClient

import app.main as main
from app.gemini_service import GeminiServiceError


client = TestClient(main.app)


class SuccessfulGeminiService:
    async def answer_question_about_image(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict[str, str]:
        assert image_bytes == b"image-bytes"
        assert image_content_type == "image/png"
        assert question == "What does the label say?"
        return {
            "answer": "The label appears to say AX-2048.",
            "model": "gemini-2.5-flash",
        }


class FailingGeminiService:
    async def answer_question_about_image(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict[str, str]:
        raise GeminiServiceError(
            "Gemini is temporarily unavailable. Please try again.",
            status_code=503,
        )


def test_ask_returns_answer_from_gemini_service(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_gemini_service", lambda: SuccessfulGeminiService())

    response = client.post(
        "/ask",
        data={"question": "What does the label say?"},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "The label appears to say AX-2048.",
        "model": "gemini-2.5-flash",
    }


def test_ask_rejects_blank_question(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_gemini_service", lambda: SuccessfulGeminiService())

    response = client.post(
        "/ask",
        data={"question": "   "},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Question must not be empty."}


def test_ask_rejects_unsupported_image_type(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_gemini_service", lambda: SuccessfulGeminiService())

    response = client.post(
        "/ask",
        data={"question": "What is shown?"},
        files={"image": ("sample.gif", b"gif-bytes", "image/gif")},
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": "Only JPEG, PNG, and WEBP images are supported."
    }


def test_ask_rejects_large_images(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_gemini_service", lambda: SuccessfulGeminiService())

    oversized_bytes = b"a" * ((5 * 1024 * 1024) + 1)
    response = client.post(
        "/ask",
        data={"question": "What is shown?"},
        files={"image": ("large.png", oversized_bytes, "image/png")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "Image must be 5 MB or smaller."}


def test_ask_returns_safe_gemini_errors(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_gemini_service", lambda: FailingGeminiService())

    response = client.post(
        "/ask",
        data={"question": "What is shown?"},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Gemini is temporarily unavailable. Please try again."
    }
