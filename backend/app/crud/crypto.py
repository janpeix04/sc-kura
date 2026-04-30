import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserKey, EncryptedFolder
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


async def get_root(
    *, session: AsyncSession, user_id: uuid.UUID
) -> EncryptedFolder | None:
    stmt = select(EncryptedFolder).where(
        (EncryptedFolder.user_id == user_id) & (EncryptedFolder.encrypted_name == "/")
    )
    result = await session.exec(stmt)
    return result.first()


async def create_folder(
    *, session: AsyncSession, folder_create: EncryptedFolder
) -> EncryptedFolder:
    folder = EncryptedFolder.model_validate(folder_create)
    session.add(folder)
    await session.commit()
    await session.refresh(folder)
    return folder
