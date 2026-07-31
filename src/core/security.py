from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.core.settings import settings

pwd_context_manager = CryptContext(schemes=["bcrypt"])

SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MIN: int = settings.ACCESS_TOKEN_EXPIRE_MIN


def hash_password(password: str) -> str:
    return pwd_context_manager.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context_manager.verify(plain_password, hashed_password)


def create_access_token(subject: str, email: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode = {"sub": subject, "email": email, "type": "access", "exp": expires}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
