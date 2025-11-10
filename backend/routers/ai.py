from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import json
from backend.ai import call_groq_insights
from backend.database import get_db
from backend.models.upload import Upload
from backend.utils import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Insights"])

@router.post("/insights/{upload_id}")
def ai_insights(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    upload_rec = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    if not upload_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    summary_path = f"{upload_rec.filepath}.summary.json"
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=400, detail="Summary not available; please generate summary first")

    with open(summary_path, "r") as f:
        summary = json.load(f)

    prompt = f"Analyze this dataset summary and give 3 key insights:\n{json.dumps(summary, indent=2)}"
    try:
        insights = call_groq_insights(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI API error: {str(e)}")

    return {"upload_id": upload_id, "insights": insights}
