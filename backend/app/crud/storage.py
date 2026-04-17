import uuid
import re

from datetime import datetime, timezone

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app import utils
from app.models import File, Folder
from app.schemas.storage import FileCreate, FolderCreate, FileStatus, FolderStatus


async def get_folder_by_id(
    *, session: AsyncSession, folder_id: uuid.UUID
) -> Folder | None:
    stmt = select(Folder).where(Folder.id == folder_id)
    result = await session.exec(stmt)
    return result.first()


async def get_folders_in_folder(
    *,
    session: AsyncSession,
    parent_id: uuid.UUID,
    status: FolderStatus | None = None,
) -> list[Folder]:
    stmt = select(Folder).where((Folder.parent_id == parent_id))

    if status is not None:
        stmt = stmt.where(Folder.status == status)

    results = await session.exec(stmt)
    return results.all()


async def get_root_folder(
    *, session: AsyncSession, user_id: uuid.UUID
) -> Folder | None:
    stmt = select(Folder).where(
        (Folder.name == "/") & (Folder.location == "/") & (Folder.user_id == user_id)
    )
    result = await session.exec(stmt)
    return result.first()


async def get_trash_folder(
    *, session: AsyncSession, user_id: uuid.UUID
) -> Folder | None:
    stmt = select(Folder).where(
        (Folder.name == "trash/")
        & (Folder.location == "/")
        & (Folder.user_id == user_id)
    )
    result = await session.exec(stmt)
    return result.first()


async def create_folder(
    *, session: AsyncSession, folder_create: FolderCreate
) -> Folder:
    folder = Folder.model_validate(folder_create)
    session.add(folder)
    await session.commit()
    await session.refresh(folder)
    return folder


async def count_folder_with_name(
    *, session: AsyncSession, name: str, parent_id: uuid.UUID | None = None
) -> int:
    stmt = select(Folder.name)
    if parent_id is not None:
        stmt = stmt.where(Folder.parent_id == parent_id)

    results = await session.exec(stmt)
    folder_names = results.all()

    pattern = re.compile(rf"^{re.escape(name)}(?: \(\d+\))?$")
    count = sum(1 for n in folder_names if pattern.match(n))
    return count


async def update_folder(*, session: AsyncSession, folder_in: Folder, **fields) -> None:
    for key, value in fields.items():
        setattr(folder_in, key, value)
    await session.commit()


async def update_folder_tree_location(
    *, session: AsyncSession, folder_in: Folder
) -> None:
    files = await get_files_in_folder(session=session, folder_id=folder_in.id)

    for file in files:
        await update_file_location(session=session, file=file, location=folder_in.name)

    subfolders = await get_folders_in_folder(session=session, parent_id=folder_in.id)

    for subfolder in subfolders:
        subfolder.location = folder_in.name
        subfolder.modified_at = datetime.now(timezone.utc)

    await session.commit()


async def rename_folder(
    *, session: AsyncSession, folder: Folder, new_name: str
) -> None:
    folder.name = new_name
    folder.modified_at = datetime.now(timezone.utc)
    session.add(folder)
    await session.flush()
    await update_folder_tree_location(session=session, folder_in=folder)
    await session.commit()


async def update_folder_tree_status(
    *,
    session: AsyncSession,
    folder_in: Folder,
    status: FolderStatus = FolderStatus.UPLOADED,
) -> None:
    files = await get_files_in_folder(session=session, folder_id=folder_in.id)

    for file in files:
        await update_file_status(session=session, file=file, status=status)

    subfolders = await get_folders_in_folder(session=session, parent_id=folder_in.id)

    for subfolder in subfolders:
        subfolder.status = status
        subfolder.modified_at = datetime.now(timezone.utc)

        session.add(subfolder)
        await update_folder_tree_status(
            session=session, folder_in=subfolder, status=status
        )

    await session.commit()


async def update_folder_status(
    *,
    session: AsyncSession,
    folder: Folder,
    status: FolderStatus = FolderStatus.UPLOADED,
) -> None:
    folder.status = status
    folder.modified_at = datetime.now(timezone.utc)
    session.add(folder)
    await update_folder_tree_status(session=session, folder_in=folder, status=status)
    await session.commit()


async def get_suggested_folders(
    *, session: AsyncSession, user_id: uuid.UUID
) -> list[Folder]:
    folders = await session.exec(
        select(Folder).where(
            (Folder.user_id == user_id)
            & (Folder.parent_id.isnot(None) & (Folder.status == FolderStatus.UPLOADED))
        )
    )
    now = datetime.now(timezone.utc)

    sorted_folders = sorted(folders, key=lambda f: utils.score(f, now), reverse=True)
    return sorted_folders[:10]


async def get_suggested_files(
    *, session: AsyncSession, user_id: uuid.UUID
) -> list[File]:
    files = await session.exec(
        select(File).where(
            (File.user_id == user_id)
            & (File.parent_id.isnot(None))
            & (File.status == FileStatus.UPLOADED)
        )
    )
    now = datetime.now(timezone.utc)

    sorted_files = sorted(files, key=lambda f: utils.score(f, now), reverse=True)
    return sorted_files[:30]


async def get_files_in_folder(
    *,
    session: AsyncSession,
    folder_id: uuid.UUID,
    status: FileStatus = FileStatus.UPLOADED,
) -> list[File]:
    stmt = select(File).where((File.parent_id == folder_id) & (File.status == status))
    results = await session.exec(stmt)
    return results.all()


async def update_folder_size_chain(
    *,
    session: AsyncSession,
    folder_id: uuid.UUID | None,
    size_delta: int,
) -> None:
    while folder_id is not None:
        folder = await get_folder_by_id(session=session, folder_id=folder_id)

        if folder is None:
            break

        print(folder)

        folder.size += size_delta
        folder.modified_at = datetime.now(timezone.utc)

        session.add(folder)
        folder_id = folder.parent_id

    await session.commit()


async def create_file(*, session: AsyncSession, file_create: FileCreate) -> File:
    file = File.model_validate(file_create)
    session.add(file)
    await session.flush()
    await update_folder_size_chain(
        session=session, folder_id=file.parent_id, size_delta=file.size
    )
    await session.commit()
    await session.refresh(file)
    return file


async def get_file_by_id(*, session: AsyncSession, file_id: uuid.UUID) -> File | None:
    stmt = select(File).where(File.id == file_id)
    result = await session.exec(stmt)
    return result.first()


async def delete_file(*, session: AsyncSession, file: File) -> None:
    stmt = delete(File).where((File.id == file.id) & (File.user_id == file.user_id))
    await update_folder_size_chain(
        session=session, folder_id=file.parent_id, size_delta=-file.size
    )
    await session.exec(stmt)
    await session.commit()


async def update_file_status(
    *, session: AsyncSession, file: File, status: FileStatus = FileStatus.UPLOADED
) -> None:
    file.status = status
    file.modified_at = datetime.now(timezone.utc)
    session.add(file)
    await session.commit()


async def update_file_location(
    *, session: AsyncSession, file: File, location: str
) -> None:
    file.location = location
    file.modified_at = datetime.now(timezone.utc)
    session.add(file)
    await session.commit()


async def rename_file(*, session: AsyncSession, file: File, new_name: str) -> None:
    file.name = new_name
    file.modified_at = datetime.now(timezone.utc)
    session.add(file)
    await session.commit()


async def get_likely_folders(
    *, session: AsyncSession, user_id: uuid.UUID, query: str
) -> list[Folder]:
    stmt = select(Folder).where(
        (Folder.user_id == user_id)
        & (Folder.status == FolderStatus.UPLOADED)
        & (Folder.name != "/")
        & (Folder.name.ilike(f"%{query}%"))
    )
    results = await session.exec(stmt)
    return results.all()


async def get_likely_files(
    *, session: AsyncSession, user_id: uuid.UUID, query: str
) -> list[File]:
    stmt = select(File).where(
        (File.user_id == user_id)
        & (File.status == FileStatus.UPLOADED)
        & (File.name.ilike(f"%{query}%"))
    )
    results = await session.exec(stmt)
    return results.all()


async def get_all_files_by_status(
    *,
    session: AsyncSession,
    user_id: uuid.UUID,
    status: FileStatus = FileStatus.UPLOADED,
) -> list[File]:
    stmt = select(File).where((File.user_id == user_id) & (File.status == status))
    results = await session.exec(stmt)
    return results.all()


async def delete_folder(*, session: AsyncSession, folder: Folder) -> None:
    stmt = delete(Folder).where(
        (Folder.id == folder.id) & (Folder.user_id == folder.user_id)
    )
    await update_folder_size_chain(
        session=session,
        folder_id=folder.parent_id,
        size_delta=-folder.size,
    )
    await session.exec(stmt)
    await session.commit()
