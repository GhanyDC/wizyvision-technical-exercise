from fastapi import HTTPException, UploadFile, status


def validate_question(question: str) -> str:
    cleaned_question = question.strip()
    if not cleaned_question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question must not be empty.",
        )

    return cleaned_question


async def read_and_validate_image(
    *,
    image: UploadFile,
    max_upload_size_bytes: int,
) -> bytes:
    if not image.filename or not image.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image file is required.",
        )

    content_type = (image.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only image uploads are supported.",
        )

    total_size = 0
    chunks: list[bytes] = []

    while True:
        chunk = await image.read(1024 * 1024)
        if not chunk:
            break

        total_size += len(chunk)
        if total_size > max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"Image must be {max_upload_size_bytes // (1024 * 1024)} MB "
                    "or smaller."
                ),
            )

        chunks.append(chunk)

    file_bytes = b"".join(chunks)
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image file must not be empty.",
        )

    return file_bytes
