from fastapi import APIRouter

from app.deps.auth import SessionDep, CurrentUser
from app.deps.storage import ValidatedFolder
from app.i18n import _
from app.crud import storage as storage_crud
from app.schemas.storage import FolderPublic, FolderCreate
from app.schemas.utils import HTTPError, add_responses

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/folder/root/", response_model=FolderPublic, responses=add_responses(404))
async def get_root_folder(
    session: SessionDep, current_user: CurrentUser
) -> FolderPublic:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(404, _("Root folder not found"))
    return FolderPublic(
        id=root.id,
        name=root.name,
        path=root.path,
        type=root.type,
        size=root.size,
        owner=f"{current_user.first_name} {current_user.last_name}",
        modified_at=root.modified_at,
        opened_at=root.opened_at,
        created_at=root.created_at,
    )


@router.post("/folder/root/", response_model=str)
async def create_root_folder(session: SessionDep, current_user: CurrentUser) -> str:
    folder_create = FolderCreate(
        name="/",
        path="/",
        user_id=current_user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Root folder created successfully")


@router.get("/folders/{folder_id}/", response_model=FolderPublic)
async def get_folders_in_folder(
    session: SessionDep, folder_in: ValidatedFolder
) -> FolderPublic:
    folders = await storage_crud.get_folders_in_folders(
        session=session, parent_id=folder_in.id
    )
    return folders


@router.get("/folder/root/", response_model=FolderPublic, responses=add_responses(404))
async def get_root_folder(
    session: SessionDep, current_user: CurrentUser
) -> FolderPublic:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(404, _("Root folder not found"))
    return FolderPublic(
        id=root.id,
        name=root.name,
        path=root.path,
        type=root.type,
        size=root.size,
        owner=f"{current_user.first_name} {current_user.last_name}",
        modified_at=root.modified_at,
        opened_at=root.opened_at,
        created_at=root.created_at,
    )


@router.post("/folder/root/", response_model=str)
async def create_root_folder(session: SessionDep, current_user: CurrentUser) -> str:
    folder_create = FolderCreate(
        name="/",
        path="/",
        owner=f"{current_user.first_name} {current_user.last_name}",
        user_id=current_user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Root folder created successfully")
