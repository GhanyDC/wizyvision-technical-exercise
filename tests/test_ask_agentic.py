from fastapi.testclient import TestClient

import app.main as main
from app.gemini_service import GeminiServiceError


client = TestClient(main.app)


class SuccessfulAgenticGeminiService:
    async def answer_question_about_image_agentic(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict:
        assert image_bytes == b"image-bytes"
        assert image_content_type == "image/png"
        assert question == "Count the visible pedals."
        return {
            "answer": "There are 3 visible pedals.",
            "model": "gemini-3-flash-preview",
            "mode": "agentic",
            "timeline": [
                {
                    "type": "think",
                    "content": "The pedal board is small, so zooming in will help.",
                },
                {
                    "type": "act",
                    "language": "python",
                    "code": "print('zoom')",
                },
                {
                    "type": "observe",
                    "output": "zoom",
                    "outcome": "outcome_ok",
                },
            ],
        }


class FailingAgenticGeminiService:
    async def answer_question_about_image_agentic(
        self,
        *,
        image_bytes: bytes,
        image_content_type: str,
        question: str,
    ) -> dict:
        raise GeminiServiceError(
            "Gemini is temporarily unavailable. Please try again.",
            status_code=503,
        )


def test_ask_agentic_returns_timeline(monkeypatch) -> None:
    monkeypatch.setattr(main, "generate_request_id", lambda: "req_test2001")
    monkeypatch.setattr(
        main,
        "get_gemini_service",
        lambda: SuccessfulAgenticGeminiService(),
    )

    response = client.post(
        "/ask-agentic",
        data={"question": "Count the visible pedals."},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "There are 3 visible pedals.",
        "model": "gemini-3-flash-preview",
        "mode": "agentic",
        "request_id": "req_test2001",
        "timeline": [
            {
                "type": "think",
                "content": "The pedal board is small, so zooming in will help.",
                "language": None,
                "code": None,
                "output": None,
                "outcome": None,
                "mime_type": None,
                "data": None,
            },
            {
                "type": "act",
                "content": None,
                "language": "python",
                "code": "print('zoom')",
                "output": None,
                "outcome": None,
                "mime_type": None,
                "data": None,
            },
            {
                "type": "observe",
                "content": None,
                "language": None,
                "code": None,
                "output": "zoom",
                "outcome": "outcome_ok",
                "mime_type": None,
                "data": None,
            },
        ],
}


def test_ask_agentic_rejects_blank_question(monkeypatch) -> None:
    monkeypatch.setattr(main, "generate_request_id", lambda: "req_test2002")
    monkeypatch.setattr(
        main,
        "get_gemini_service",
        lambda: SuccessfulAgenticGeminiService(),
    )

    response = client.post(
        "/ask-agentic",
        data={"question": "   "},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Question must not be empty.",
        "request_id": "req_test2002",
    }


def test_ask_agentic_rejects_unsupported_image_type(monkeypatch) -> None:
    monkeypatch.setattr(main, "generate_request_id", lambda: "req_test2003")
    monkeypatch.setattr(
        main,
        "get_gemini_service",
        lambda: SuccessfulAgenticGeminiService(),
    )

    response = client.post(
        "/ask-agentic",
        data={"question": "Count the visible pedals."},
        files={"image": ("sample.gif", b"gif-bytes", "image/gif")},
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": "Only JPEG, PNG, and WEBP images are supported.",
        "request_id": "req_test2003",
    }


def test_ask_agentic_rejects_large_images(monkeypatch) -> None:
    monkeypatch.setattr(main, "generate_request_id", lambda: "req_test2004")
    monkeypatch.setattr(
        main,
        "get_gemini_service",
        lambda: SuccessfulAgenticGeminiService(),
    )

    oversized_bytes = b"a" * ((5 * 1024 * 1024) + 1)
    response = client.post(
        "/ask-agentic",
        data={"question": "Count the visible pedals."},
        files={"image": ("large.png", oversized_bytes, "image/png")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Image must be 5 MB or smaller.",
        "request_id": "req_test2004",
    }


def test_ask_agentic_returns_safe_gemini_errors(monkeypatch) -> None:
    monkeypatch.setattr(main, "generate_request_id", lambda: "req_test2005")
    monkeypatch.setattr(
        main,
        "get_gemini_service",
        lambda: FailingAgenticGeminiService(),
    )

    response = client.post(
        "/ask-agentic",
        data={"question": "Count the visible pedals."},
        files={"image": ("sample.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Gemini is temporarily unavailable. Please try again.",
        "request_id": "req_test2005",
    }
