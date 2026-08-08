import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import hash_password
from src.models.user import User
from src.schemas.user import UserCreate
from src.utils.generate_avatar import get_avatar_text


class UserServices:
    async def get_by_email(self, email: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    async def get_by_id(self, user_id: uuid.UUID, session: AsyncSession) -> User | None:
        return await session.get(User, user_id)

    async def create(self, new_user: UserCreate, session: AsyncSession) -> User:
        user = User(
            email=new_user.email,
            full_name=new_user.full_name,
            password_hash=hash_password(new_user.password),
            avatar_url=get_avatar_text(new_user.full_name),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
