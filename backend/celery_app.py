from celery import Celery

celery_app = Celery(
    "ai_dash",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["backend.tasks.data_tasks"] 
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  
    task_soft_time_limit=25 * 60  
)

celery_app.autodiscover_tasks(["backend.tasks"], force=True)
