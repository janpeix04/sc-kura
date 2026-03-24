import uuid
from pydantic import EmailStr

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import User
from app.core.security import get_password_hash, verify_password
from app.schemas.users import UserCreate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(*, session: AsyncSession, user: User, **fields) -> None:
    for key, value in fields.items():
        setattr(user, key, value)
    await session.commit()
    return


async def delete_user(*, session: AsyncSession, user_id: uuid.UUID) -> None:
    db_user = await session.get(User, user_id)
    await session.delete(db_user)
    await session.commit()
    return


async def get_user_by_email(*, session: AsyncSession, email: EmailStr) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.exec(stmt)
    return result.first()


async def authenticate_user(
    *, session: AsyncSession, email: EmailStr, password: str
) -> User | None:
    user = await get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
