# helpers/files.py
import io, uuid, datetime
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / "media"

def ext_by_ct(ct: str) -> str | None:
    return {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(ct)

async def save_image(img: UploadFile, max_mb: int = 20) -> str:
    if not img.content_type or not img.content_type.startswith("image/"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only images allowed")

    ext = ext_by_ct(img.content_type)
    if not ext:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported image type")

    raw = await img.read()
    if len(raw) > max_mb * 1024 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large")

    # проверим, что это реально картинка
    try:
        Image.open(io.BytesIO(raw)).verify()
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid image")

    # media/YYYY/MM/DD/uuid.ext
    subdir = MEDIA_ROOT / datetime.date.today().strftime("%Y/%m/%d")
    subdir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_location = subdir / filename

    async with aiofiles.open(file_location, "wb") as f:
        await f.write(raw)

    relative_path = file_location.relative_to(BASE_DIR)
    return str(relative_path).replace("\\", "/")
