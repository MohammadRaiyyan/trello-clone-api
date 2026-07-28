from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


@app.get("/health")
def health():
    return {"message": "ok"}
