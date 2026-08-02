from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    root_path="/api/v1/",
)


@app.get("/health")
def health():
    return {"message": "ok"}
