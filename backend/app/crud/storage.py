from typing import List
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.storage import FolderCreate, FileCreate, FileFolderStatus
from app.models import Folder, File
from app.api.file_services import extract_folders_from_filename


async def create_folder(
    *, session: AsyncSession, folder_create: FolderCreate
) -> Folder:
    db_folder = Folder(**folder_create.model_dump())
    session.add(db_folder)
    await session.commit()
    return db_folder


async def create_file(*, session: AsyncSession, file_create: FileCreate) -> File:
    db_file = File(**file_create.model_dump())
    session.add(db_file)
    await session.commit()
    return db_file


async def get_folder_by_path(session: AsyncSession, path: str, user_id: str) -> Folder:
    stmt = select(Folder).where((Folder.path == path) & (Folder.user_id == user_id))
    results = await session.exec(stmt)
    return results.first()


async def ensure_folder_tree(
    *, session: AsyncSession, base_path: str, file_path: str, user_id: str
) -> Folder:
    folders = extract_folders_from_filename(file_path)

    current_path = base_path
    parent = await get_folder_by_path(
        session=session, path=current_path, user_id=user_id
    )

    if not folders:
        return parent

    for folder_name in folders:
        new_path = (
            f"{current_path}/{folder_name}"
            if current_path != "/"
            else f"/{folder_name}"
        )

        folder = await get_folder_by_path(
            session=session, path=new_path, user_id=user_id
        )

        if not folder:
            folder_create = FolderCreate(
                original_name=folder_name.split("/")[-1],
                stored_name=folder_name,
                path=new_path,
                status=FileFolderStatus.UPLOADED,
                user_id=user_id,
                parent_id=parent.id,
            )

            folder = await create_folder(session=session, folder_create=folder_create)
        parent = folder
        current_path = new_path
    return parent


async def get_folder_in_folders(
    *,
    session: AsyncSession,
    folder_id: str,
    user_id: str,
    status: FileFolderStatus = FileFolderStatus.UPLOADED,
) -> List[Folder]:
    stmt = select(Folder).where(
        (Folder.parent_id == folder_id)
        & (Folder.user_id == user_id)
        & (Folder.status == status)
    )
    results = await session.exec(stmt)
    return results.all()


async def get_files_in_folders(
    *,
    session: AsyncSession,
    folder_id: str,
    user_id: str,
    status: FileFolderStatus = FileFolderStatus.UPLOADED,
) -> List[File]:
    stmt = select(File).where(
        (File.folder_id == folder_id)
        & (File.user_id == user_id)
        & (File.status == status)
    )
    results = await session.exec(stmt)
    return results.all()


async def get_folder_by_folder_id(*, session: AsyncSession, folder_id: str) -> Folder:
    stmt = select(Folder).where(Folder.id == folder_id)
    result = await session.exec(stmt)
    return result.first()


async def update_folder_size_recursive(
    *, session: AsyncSession, folder: Folder, size: int
) -> None:
    current_folder = folder

    while current_folder:
        current_folder.size += size

        if not current_folder.parent_id:
            break

        current_folder = await get_folder_by_folder_id(
            session=session, folder_id=current_folder.parent_id
        )
    await session.commit()


async def get_user_storage_used(*, session: AsyncSession, user_id: str) -> int:
    stmt = select(func.sum(File.size)).where(File.user_id == user_id)
    result = await session.exec(stmt)
    return result.one() or 0


async def get_folder_in_path(
    *, session: AsyncSession, folder_name: str, path: str, user_id: str | None = None
) -> Folder | None:
    stmt = select(Folder).where(
        (Folder.original_name == folder_name) & (Folder.path == path)
    )
    if user_id is None:
        stmt = stmt.where(Folder.user_id == user_id)

    result = await session.exec(stmt)
    return result.first()


async def get_file_in_folder(
    *, session: AsyncSession, folder_id: str, file_name: str, user_id: str
) -> File | None:
    stmt = select(File).where(
        (File.folder_id == folder_id)
        & (File.original_name == file_name)
        & (File.user_id == user_id)
    )
    result = await session.exec(stmt)
    return result.first()
