from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.models
from src.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Trello Clone API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"message": "ok"}
