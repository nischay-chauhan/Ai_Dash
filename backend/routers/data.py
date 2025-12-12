import pandas as pd
import numpy as np
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

    def clean_for_json(data):
        if isinstance(data, dict):
            return {k: clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [clean_for_json(v) for v in data]
        elif isinstance(data, float):
            if np.isnan(data) or np.isinf(data):
                return None
            return data
        return data

    stats_df = df.describe(include='all')
    stats_dict = stats_df.where(pd.notnull(stats_df), None).to_dict()
    
    summary = {
        "filename": upload_record.filename,
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "stats": clean_for_json(stats_dict),
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": df.select_dtypes(exclude="number").columns.tolist(),
    }

    if len(summary["numeric_columns"]) >= 2:
        corr = df[summary["numeric_columns"]].corr().round(3)
        summary["correlation"] = clean_for_json(corr.where(pd.notnull(corr), None).to_dict())

    sample_data = df.head(5).where(pd.notnull(df), None).to_dict(orient="records")
    summary["sample_data"] = clean_for_json(sample_data)

    return summary


@router.get("/content/{upload_id}")
def get_data_content(
    upload_id: int,
    limit: int = 10000,
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
        df = pd.read_csv(file_path, nrows=limit)
        
        df = df.where(pd.notnull(df), None)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
