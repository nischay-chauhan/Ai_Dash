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

    try:
        df = pd.read_csv(file_path)
        summary = {
            "filename": upload_record.filename,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "stats": df.describe(include='all').fillna("").to_dict(),
            "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
            "categorical_columns": df.select_dtypes(exclude="number").columns.tolist(),
        }

        if len(summary["numeric_columns"]) >= 2:
            corr = df[summary["numeric_columns"]].corr().round(3).to_dict()
            summary["correlation"] = corr

        summary["sample_data"] = df.head(5).to_dict(orient="records")
        summary_json = json.dumps(summary)

        new_summary = Summary(
            upload_id=upload_record.id,
            user_id=current_user.id,
            summary_json=summary_json
        )
        db.add(new_summary)
        db.commit()

    except Exception as e:
        print(f"Error generating summary: {str(e)}")

    return {
        "message": "File uploaded successfully",
        "metadata": {
            "id": upload_record.id,
            "filename": upload_record.filename,
            "size": upload_record.size,
            "uploaded_at": upload_record.uploaded_at,
        },
    }
