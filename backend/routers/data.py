import pandas as pd
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.upload import Upload
from backend.utils import get_current_user

router = APIRouter(prefix="/data", tags=["Data Summary"])


@router.get("/summary/{upload_id}")
def get_data_summary(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    upload_record = db.query(Upload).filter(
        Upload.id == upload_id, Upload.user_id == current_user.id
    ).first()

    if not upload_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    file_path = upload_record.filepath
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing on disk")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

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
        corr = df[summary["numeric_columns"]].corr().round(3)
        summary["correlation"] = corr.where(pd.notnull(corr), None).to_dict()

    summary["sample_data"] = df.head(5).where(pd.notnull(df), None).to_dict(orient="records")

    return summary
