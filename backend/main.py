from fastapi import FastAPI
from backend.database import Base , engine
from backend.models import User
from backend.routers import auth
import backend.routers.upload as upload
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI_Dash")
app.include_router(auth.router)
app.include_router(upload.router)


