from fastapi import APIRouter

from src.schemas.user import UserLogin

auth_router = APIRouter(prefix="auth")

auth_router.post("/login")
async def login(creds:UserLogin)->:
