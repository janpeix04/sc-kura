import uuid

from sqlmodel import select, delete, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserKey, EncryptedFolder, EncryptedFile
from app.schemas.users import UserKeyCreate
from app.schemas.storage import FolderStatus, FileStatus
from app.schemas.crypto import (
    EncryptedFolderRename,
    EncryptedFileCreate,
    EncryptedFileRename,
)


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


async def get_files_in_folder(
    *,
    session: AsyncSession,
    parent_id: uuid.UUID,
    status: FileStatus | None = None,
) -> list[EncryptedFile]:
    stmt = select(EncryptedFile).where((EncryptedFile.parent_id == parent_id))

    if status is not None:
        stmt = stmt.where(EncryptedFile.status == status)

    results = await session.exec(stmt)
    return results.all()


async def update_folder_size_chain(
    *,
    session: AsyncSession,
    folder_id: uuid.UUID | None,
    size_delta: int,
) -> None:
    while folder_id is not None:
        await session.exec(
            update(EncryptedFolder)
            .where(EncryptedFolder.id == folder_id)
            .values(
                size=EncryptedFolder.size + size_delta,
            )
        )

        result = await session.exec(
            select(EncryptedFolder.parent_id).where(EncryptedFolder.id == folder_id)
        )
        folder_id = result.one_or_none()


async def delete_folder(*, session: AsyncSession, folder: EncryptedFolder) -> None:
    stmt = delete(EncryptedFolder).where(
        (EncryptedFolder.id == folder.id) & (EncryptedFolder.user_id == folder.user_id)
    )
    await update_folder_size_chain(
        session=session,
        folder_id=folder.parent_id,
        size_delta=-folder.size,
    )
    await session.exec(stmt)
    await session.commit()


async def create_file(
    *, session: AsyncSession, file_create: EncryptedFileCreate
) -> EncryptedFile:
    file = EncryptedFile.model_validate(file_create)
    session.add(file)
    await session.flush()
    await update_folder_size_chain(
        session=session, folder_id=file_create.parent_id, size_delta=file.size
    )
    await session.commit()
    await session.refresh(file)
    return file


async def get_file_by_id(
    *, session: AsyncSession, file_id: uuid.UUID
) -> EncryptedFile | None:
    stmt = select(EncryptedFile).where(EncryptedFile.id == file_id)
    result = await session.exec(stmt)
    return result.first()


async def delete_file(*, session: AsyncSession, file: EncryptedFile) -> None:
    stmt = delete(EncryptedFile).where(
        (EncryptedFile.id == file.id) & (EncryptedFile.user_id == file.user_id)
    )
    await update_folder_size_chain(
        session=session, folder_id=file.parent_id, size_delta=-file.size
    )
    await session.exec(stmt)
    await session.commit()


async def rename_file(
    *, session: AsyncSession, file: EncryptedFile, payload: EncryptedFileRename
) -> None:
    file.encrypted_name = payload.encrypted_name
    file.encrypted_name_iv = payload.iv
    session.add(file)
    await session.commit()


async def update_user_keys(
    *, session: AsyncSession, db_keys: UserKey, **fields
) -> None:
    for key, value in fields.items():
        setattr(db_keys, key, value)
    await session.commit()
