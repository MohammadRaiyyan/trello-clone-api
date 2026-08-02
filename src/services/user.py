import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import hash_password
from src.models.user import User
from src.schemas.user import UserCreate
from src.utils.generate_avatar import get_avatar_text


class UserServices:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, new_user: UserCreate) -> User:
        user = User(
            email=new_user.email,
            full_name=new_user.full_name,
            password_hash=hash_password(new_user.password),
            avatar_url=get_avatar_text(new_user.full_name),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
