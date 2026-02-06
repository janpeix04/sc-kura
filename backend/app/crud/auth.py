from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import get_password_hash


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
        },
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.exec(stmt)
    return result.first()
