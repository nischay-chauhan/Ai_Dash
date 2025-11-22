import json
import os
from typing import Any, Dict, Optional, AsyncGenerator

import pandas as pd
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from backend.models.upload import Upload
from backend.models.chat import ChatMessage
from backend.agents.data_agent import create_graph

async def stream_chat_process(db: Session, user_id: int, upload_id: int, user_question: str) -> AsyncGenerator[str, None]:
    upload: Optional[Upload] = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.user_id == user_id)
        .first()
    )
    if not upload:
        yield f"event: error\ndata: Dataset not found or access denied\n\n"
        return

    if not os.path.exists(upload.filepath):
        yield f"event: error\ndata: File missing on disk\n\n"
        return

    try:
        df = pd.read_csv(upload.filepath)
    except Exception as e:
        yield f"event: error\ndata: Failed to load CSV file: {str(e)}\n\n"
        return

    history_records = (
        db.query(ChatMessage)
        .filter(ChatMessage.upload_id == upload_id, ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(20) 
        .all()
    )

    messages = []
    for record in history_records:
        messages.append(HumanMessage(content=record.message))
        if record.response:
            messages.append(AIMessage(content=record.response))
    
    messages.append(HumanMessage(content=user_question))

    try:
        app = create_graph(df)
        
        final_response = ""
        
        async for event in app.astream_events({"messages": messages}, version="v1"):
            kind = event["event"]
            
            if kind == "on_chain_start":
                if event["name"] == "LangGraph":
                    yield f"event: agent_state\ndata: {json.dumps({'status': 'starting'})}\n\n"
            
            elif kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    final_response += content
                    yield f"event: message_chunk\ndata: {json.dumps(content)}\n\n"

            elif kind == "on_tool_start":
                yield f"event: agent_state\ndata: {json.dumps({'status': 'executing_tool', 'tool': event['name']})}\n\n"

            elif kind == "on_tool_end":
                 yield f"event: agent_state\ndata: {json.dumps({'status': 'tool_finished', 'output': str(event['data'].get('output'))})}\n\n"

        chat = ChatMessage(
            user_id=user_id,
            upload_id=upload_id,
            message=user_question,
            response=final_response,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        yield f"event: done\ndata: {json.dumps({'message_id': chat.id})}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {str(e)}\n\n"
