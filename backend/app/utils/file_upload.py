import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from app.core.config import settings

def validate_image(file: UploadFile):
    # Check file size
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="ไฟล์มีขนาดใหญ่เกิน 5MB")
    
    # Check content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="รองรับเฉพาะไฟล์รูปภาพ (JPG, PNG, WEBP) เท่านั้น")

async def save_upload_file(file: UploadFile, sub_dir: str) -> str:
    validate_image(file)
    
    # Create sub-directory
    upload_path = settings.UPLOADS_DIR / sub_dir
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = upload_path / unique_filename
    
    # Process and Save image (Resize & Compress)
    try:
        img_content = await file.read()
        img = Image.open(io.BytesIO(img_content))
        
        # Max dimensions (1200px)
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (for JPG)
        if img.mode in ("RGBA", "P") and extension.lower() in [".jpg", ".jpeg"]:
            img = img.convert("RGB")
            
        # Save optimized image
        img.save(file_path, optimize=True, quality=85)
        
    except Exception as e:
        # Fallback to simple save if processing fails
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
    return f"uploads/{sub_dir}/{unique_filename}"

def delete_physical_file(relative_path: str):
    """Deletes a file and cleans up empty parent directory."""
    full_path = settings.BASE_DIR / relative_path
    if full_path.exists() and full_path.is_file():
        parent_dir = full_path.parent
        os.remove(full_path)
        
        # Cleanup parent folder if empty
        try:
            if parent_dir != settings.UPLOADS_DIR and not any(parent_dir.iterdir()):
                os.rmdir(parent_dir)
        except Exception:
            pass # Ignore errors during cleanup
