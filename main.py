from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.core.rate_limit import limiter
from src.core.settings import settings
from src.routes.auth import auth_router
from src.routes.manifest import manifest_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    root_path="/api/v1/",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
):

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
        },
    )


app.include_router(auth_router)
app.include_router(manifest_router)


@app.get("/health")
def health():
    return {"message": "ok"}
