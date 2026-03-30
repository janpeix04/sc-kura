from fastapi import APIRouter

from app.deps.auth import SessionDep
from app.deps.storage import ValidatedFolder
from app.crud import storage as storage_crud
from app.schemas.storage import FolderPublic

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/folders/{folder_id}/", response_model=FolderPublic)
async def get_folders_in_folder(
    session: SessionDep, folder_in: ValidatedFolder
) -> FolderPublic:
    folders = await storage_crud.get_folders_in_folders(
        session=session, parent_id=folder_in.id
    )
    return folders
