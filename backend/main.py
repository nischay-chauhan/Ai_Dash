from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import auth, upload, data, ai, task_status

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI_Dash")

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(data.router)
app.include_router(ai.router)
app.include_router(task_status.router)
