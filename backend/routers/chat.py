from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.utils import get_current_user
from backend.chat_service import stream_chat_process
from backend.models.chat import ChatMessage

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    dataset_id: int
    message: str


@router.post("/", status_code=200)
async def chat(request: ChatRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return StreamingResponse(
            stream_chat_process(
                db=db,
                user_id=current_user.id,
                upload_id=request.dataset_id,
                user_question=request.message,
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")


@router.get("/history/{dataset_id}")
def history(
    dataset_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if limit > 200:
        limit = 200
    q = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.upload_id == dataset_id,
            ChatMessage.user_id == current_user.id,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    items = q.all()
    return [
        {
            "id": m.id,
            "message": m.message,
            "response": m.response,
            "created_at": m.created_at,
        }
        for m in items
    ]
