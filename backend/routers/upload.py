import os
import pandas as pd
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.upload import Upload
from backend.models.summary import Summary
from backend.utils import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"


@router.post("/", status_code=202)
async def upload_csv(
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
        uploaded_at=datetime.utcnow(),
        status="uploaded"  
    )

    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)

    from backend.tasks.data_tasks import process_file_task
    task = process_file_task.delay(upload_record.id)

    return {
        "message": "File upload accepted and processing started",
        "upload_id": upload_record.id,
        "task_id": task.id,
        "status": "processing",
        "metadata": {
            "id": upload_record.id,
            "filename": upload_record.filename,
            "size": upload_record.size,
            "uploaded_at": upload_record.uploaded_at.isoformat()
        },
    }

@router.get("/", status_code=200)
async def get_uploads(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).order_by(Upload.uploaded_at.desc()).all()
    
    return [
        {
            "id": upload.id,
            "filename": upload.filename,
            "size": upload.size,
            "uploaded_at": upload.uploaded_at,
            "status": upload.status
        }
        for upload in uploads
    ]
