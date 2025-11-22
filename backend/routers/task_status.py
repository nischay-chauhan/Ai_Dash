import asyncio
import json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
from backend.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a background task by its ID
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        response = {
            'task_id': task_id,
            'status': 'pending',
            'result': None
        }
    elif task_result.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'status': 'completed',
            'result': task_result.result
        }
    elif task_result.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'status': 'failed',
            'result': str(task_result.result),  # Error message
            'traceback': str(task_result.traceback) if task_result.traceback else None
        }
    elif task_result.state == 'PROGRESS':
        response = {
            'task_id': task_id,
            'status': 'processing',
            'result': task_result.info
        }
    else:
        response = {
            'task_id': task_id,
            'status': task_result.state.lower(),
            'result': task_result.result if task_result.ready() else None
        }
    
    return response

async def event_generator(task_id: str):
    """
    Generator for SSE events
    """
    while True:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            yield f"event: status\ndata: {json.dumps({'status': 'pending', 'percent': 0})}\n\n"
        
        elif task_result.state == 'PROGRESS':
            data = task_result.info
            yield f"event: progress\ndata: {json.dumps({'status': 'processing', 'percent': data.get('current', 0), 'message': data.get('status', '')})}\n\n"
            
        elif task_result.state == 'SUCCESS':
            yield f"event: complete\ndata: {json.dumps({'status': 'completed', 'percent': 100, 'result': task_result.result})}\n\n"
            break
            
        elif task_result.state == 'FAILURE':
            yield f"event: error\ndata: {json.dumps({'status': 'failed', 'error': str(task_result.result)})}\n\n"
            break
            
        await asyncio.sleep(1)

@router.get("/{task_id}/stream")
async def stream_task_status(task_id: str):
    """
    Stream the status of a background task using SSE
    """
    return StreamingResponse(event_generator(task_id), media_type="text/event-stream")