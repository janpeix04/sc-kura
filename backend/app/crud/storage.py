from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.storage import FolderCreate, FileCreate
from app.models import Folder, File
from app.api.file_services import extract_folders_from_filename


async def get_folder_by_path(session: AsyncSession, path: str) -> Folder:
    stmt = select(Folder).where(Folder.path == path)
    results = await session.exec(stmt)
    return results.first()


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


async def ensure_folder_tree(
    *, session: AsyncSession, base_path: str, file_path: str, user_id: str
) -> Folder:
    folders = extract_folders_from_filename(file_path)

    current_path = "/" if base_path == "/" else f"/{base_path.strip('/')}"
    parent = await get_folder_by_path(session=session, path=current_path)

    if not folders:
        return parent

    for folder_name in folders:
        new_path = (
            f"{current_path}/{folder_name}"
            if current_path != "/"
            else f"/{folder_name}"
        )

        folder = await get_folder_by_path(session=session, path=new_path)

        if not folder:
            folder_create = FolderCreate(
                original_name=folder_name.split("/")[-1],
                stored_name=folder_name,
                path=new_path,
                user_id=user_id,
                parent_id=parent.id,
            )

            folder = await create_folder(session=session, folder_create=folder_create)
        parent = folder
        current_path = new_path
    return parent


async def get_folders_by_folder_id(
    *, session: AsyncSession, folder_id: str, user_id: str
) -> List[Folder]:
    stmt = select(Folder).where(
        (Folder.parent_id == folder_id) & (Folder.user_id == user_id)
    )
    results = await session.exec(stmt)
    return results.all()


async def get_files_by_folder_id(
    *, session: AsyncSession, folder_id: str, user_id: str
) -> List[File]:
    stmt = select(File).where((File.folder_id == folder_id) & (File.user_id == user_id))
    results = await session.exec(stmt)
    return results.all()
