import uuid
import re

from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import utils
from app.models import File, Folder
from app.schemas.storage import FolderCreate


async def get_folder_by_id(
    *, session: AsyncSession, folder_id: uuid.UUID
) -> Folder | None:
    stmt = select(Folder).where(Folder.id == folder_id)
    result = await session.exec(stmt)
    return result.first()


async def get_folders_in_folders(
    *, session: AsyncSession, parent_id: uuid.UUID
) -> list[Folder]:
    stmt = select(Folder).where(Folder.parent_id == parent_id)
    results = await session.exec(stmt)
    return results.all()


async def get_root_folder(
    *, session: AsyncSession, user_id: uuid.UUID
) -> Folder | None:
    stmt = select(Folder).where((Folder.location == "/") & (Folder.user_id == user_id))
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


async def get_suggested_folders(
    *, session: AsyncSession, user_id: uuid.UUID
) -> list[Folder]:
    folders = await session.exec(
        select(Folder).where(
            (Folder.user_id == user_id) & (Folder.parent_id.isnot(None))
        )
    )
    now = datetime.now(timezone.utc)

    sorted_folders = sorted(folders, key=lambda f: utils.score(f, now), reverse=True)
    return sorted_folders[:10]


async def get_suggested_files(
    *, session: AsyncSession, user_id: uuid.UUID
) -> list[File]:
    files = await session.exec(
        select(File).where((File.user_id == user_id) & (File.parent_id.isnot(None)))
    )
    now = datetime.now(timezone.utc)

    sorted_files = sorted(files, key=lambda f: utils.score(f, now), reverse=True)
    return sorted_files[:10]
