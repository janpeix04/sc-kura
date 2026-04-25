import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserKey
from app.schemas.users import UserKeyCreate


async def create_user_key(
    *, session: AsyncSession, keys_create: UserKeyCreate
) -> UserKey:
    user_key = UserKey.model_validate(keys_create)
    session.add(user_key)
    await session.commit()
    await session.refresh(user_key)
    return user_key


async def get_user_key(*, session: AsyncSession, user_id: uuid.UUID) -> UserKey | None:
    stmt = select(UserKey).where(UserKey.user_id == user_id)
    result = await session.exec(stmt)
    return result.first()
