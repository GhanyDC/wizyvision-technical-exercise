from fastapi import HTTPException, UploadFile, status


ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def validate_question(question: str | None) -> str:
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Question is required.",
        )

    cleaned_question = question.strip()
    if not cleaned_question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Question must not be empty.",
        )

    return cleaned_question


async def read_and_validate_image(
    *,
    image: UploadFile | None,
    max_upload_size_bytes: int,
) -> bytes:
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Image file is required.",
        )

    if not image.filename or not image.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Image file is required.",
        )

    content_type = (image.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WEBP images are supported.",
        )

    total_size = 0
    chunks: list[bytes] = []

    try:
        while True:
            chunk = await image.read(1024 * 1024)
            if not chunk:
                break

            total_size += len(chunk)
            if total_size > max_upload_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        f"Image must be {max_upload_size_bytes // (1024 * 1024)} MB "
                        "or smaller."
                    ),
                )

            chunks.append(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image could not be read.",
        ) from exc

    file_bytes = b"".join(chunks)
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Image file must not be empty.",
        )

    return file_bytes
