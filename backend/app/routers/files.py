import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from PIL import Image
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.entities import User, FileModel
from app.schemas.schemas import FileResponse

router = APIRouter(prefix="/files", tags=["Files"])

def detect_media_type(mime: str) -> Optional[str]:
    if mime.startswith("image/"):
        return "image"
    elif mime.startswith("video/"):
        return "video"
    elif mime.startswith("audio/"):
        return "audio"
    return None

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    extension = Path(file.filename).suffix if file.filename else ""
    unique_key = f"{uuid.uuid4().hex}{extension}"
    file_path = settings.UPLOAD_DIR / unique_key

    # Save to disk
    contents = await file.read()
    size_bytes = len(contents)

    with open(file_path, "wb") as f:
        f.write(contents)

    mime_type = file.content_type or "application/octet-stream"
    media_type = detect_media_type(mime_type)
    width = None
    height = None
    thumbnail_file_id = None

    # Process image dimensions and generate thumbnail
    if media_type == "image":
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                # Generate thumbnail
                thumb_img = img.copy()
                thumb_img.thumbnail((300, 300))
                thumb_key = f"thumb_{unique_key}"
                thumb_path = settings.UPLOAD_DIR / thumb_key
                thumb_img.save(thumb_path)
                thumb_size = thumb_path.stat().st_size
                thumb_w, thumb_h = thumb_img.size

                # Save parent file first
                parent_file = FileModel(
                    storage_key=unique_key,
                    original_name=file.filename or "unknown",
                    mime_type=mime_type,
                    size_bytes=size_bytes,
                    media_type=media_type,
                    width=width,
                    height=height
                )
                db.add(parent_file)
                db.commit()
                db.refresh(parent_file)

                # Save thumbnail file with thumbnail_parent_id
                thumb_model = FileModel(
                    storage_key=thumb_key,
                    original_name=f"thumb_{file.filename}",
                    mime_type=mime_type,
                    size_bytes=thumb_size,
                    media_type="image",
                    width=thumb_w,
                    height=thumb_h,
                    thumbnail_parent_id=parent_file.id
                )
                db.add(thumb_model)
                db.commit()
                return parent_file

        except Exception:
            # If image parsing fails, proceed as normal file
            pass

    # Generic file
    db_file = FileModel(
        storage_key=unique_key,
        original_name=file.filename or "unknown",
        mime_type=mime_type,
        size_bytes=size_bytes,
        media_type=media_type,
        width=width,
        height=height
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file
