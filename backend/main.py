from fastapi import FastAPI
from backend.database import Base , engine
from backend.models import User
from backend.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI_Dash")
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}