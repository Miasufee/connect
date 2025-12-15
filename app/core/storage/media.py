from __future__ import annotations

import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.response.exceptions import Exceptions
from app.core.utils.settings import settings

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
BASE_PATH = Path("media/zawiya/avatars")


async def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise Exceptions.bad_request("Invalid image type")

    BASE_PATH.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    file_path = BASE_PATH / filename

    content = await file.read()
    file_path.write_bytes(content)

    return str(file_path)

def media_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"{settings.MEDIA_BASE_URL}{path.replace('media/', '')}"
