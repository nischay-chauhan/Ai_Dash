import json
import os
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy.orm import Session

from backend.ai import call_groq_insights
from backend.models.upload import Upload
from backend.models.summary import Summary
from backend.models.chat import ChatMessage


def _build_context_from_summary(summary_record: Summary) -> Dict[str, Any]:
    try:
        return json.loads(summary_record.summary_json)
    except Exception:
        return {}


def _build_minimal_context_from_file(file_path: str) -> Dict[str, Any]:
    df = pd.read_csv(file_path)
    context = {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "sample_data": df.head(5).to_dict(orient="records"),
    }
    return context


def process_query(db: Session, user_id: int, upload_id: int, user_question: str) -> Dict[str, Any]:
    upload: Optional[Upload] = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.user_id == user_id)
        .first()
    )
    if not upload:
        raise ValueError("Dataset not found or access denied")

    if not os.path.exists(upload.filepath):
        raise FileNotFoundError("File missing on disk")

    summary_record: Optional[Summary] = (
        db.query(Summary)
        .filter(Summary.upload_id == upload_id, Summary.user_id == user_id)
        .first()
    )

    if summary_record:
        context = _build_context_from_summary(summary_record)
    else:
        context = _build_minimal_context_from_file(upload.filepath)

    prompt = (
        "You are a helpful data assistant. Answer the user's question using only the provided dataset context.\n"
        "If the answer is not derivable from the context, say so briefly.\n"
        f"Dataset metadata and sample:\n{json.dumps(context, indent=2)}\n"
        f"User asks: {user_question}\n"
        "Provide a concise, clear answer in natural language."
    )

    answer = call_groq_insights(prompt)

    chat = ChatMessage(
        user_id=user_id,
        upload_id=upload_id,
        message=user_question,
        response=answer,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return {"response": answer, "data": None, "message_id": chat.id}
