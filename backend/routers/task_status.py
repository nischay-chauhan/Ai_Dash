from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
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
    else:  # 'STARTED', 'RETRY', etc.
        response = {
            'task_id': task_id,
            'status': task_result.state.lower(),
            'result': task_result.result if task_result.ready() else None
        }
    
    return response