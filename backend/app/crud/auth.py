import uuid

from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models import User
from app.core.security import get_password_hash
from app.schemas.users import UserCreate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(user)
    await session.commit()
    await session.refresh()
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
