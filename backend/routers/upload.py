import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.upload import Upload
from backend.utils import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"


@router.post("/", status_code=201)
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only CSV files allowed"
        )

    existing_upload = db.query(Upload).filter(
        Upload.user_id == current_user.id,
        Upload.filename == file.filename
    ).first()
    
    if existing_upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File '{file.filename}' already exists in your uploads"
        )

    user_folder = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    size = os.path.getsize(file_path)
    upload_record = Upload(
        user_id=current_user.id,
        filename=file.filename,
        filepath=file_path,
        size=size,
        uploaded_at=datetime.utcnow()
    )

    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)

    return {
        "message": "File uploaded successfully",
        "metadata": {
            "id": upload_record.id,
            "filename": upload_record.filename,
            "size": upload_record.size,
            "uploaded_at": upload_record.uploaded_at,
        },
    }
