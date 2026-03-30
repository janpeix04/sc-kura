import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Folder


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
