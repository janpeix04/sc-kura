import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserKey, EncryptedFolder
from app.schemas.users import UserKeyCreate
from app.schemas.storage import FolderStatus
from app.schemas.crypto import EncryptedFolderRename


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


async def get_folder_by_id(
    *, session: AsyncSession, folder_id: uuid.UUID
) -> EncryptedFolder | None:
    stmt = select(EncryptedFolder).where(EncryptedFolder.id == folder_id)
    result = await session.exec(stmt)
    return result.first()


async def get_folders_in_folder(
    *,
    session: AsyncSession,
    parent_id: uuid.UUID,
    status: FolderStatus | None = None,
) -> list[EncryptedFolder]:
    stmt = select(EncryptedFolder).where((EncryptedFolder.parent_id == parent_id))

    if status is not None:
        stmt = stmt.where(EncryptedFolder.status == status)

    results = await session.exec(stmt)
    return results.all()


async def rename_folder(
    *, session: AsyncSession, folder_in: EncryptedFolder, payload: EncryptedFolderRename
) -> None:
    folder_in.encrypted_name = payload.encrypted_name
    folder_in.iv = payload.iv
    session.add(folder_in)
    await session.commit()
