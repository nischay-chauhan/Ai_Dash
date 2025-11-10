from fastapi import FastAPI
from backend.database import Base , engine
from backend.models import User
from backend.routers import auth, upload, data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI_Dash")
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(data.router)


