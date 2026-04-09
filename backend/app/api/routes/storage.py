from typing import Annotated

from fastapi import APIRouter, Form

from app.deps.auth import SessionDep, CurrentUser
from app.deps.storage import ValidatedFolder, ValidatedNewFolder
from app.i18n import _
from app.crud import storage as storage_crud
from app.schemas.storage import FolderPublic, FolderCreate, FolderUpdate, Breadcrumbs
from app.schemas.utils import HTTPError, add_responses

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/folders/{folder_id}/", response_model=list[FolderPublic])
async def get_folders_in_folder(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> list[FolderPublic]:
    folders = await storage_crud.get_folders_in_folders(
        session=session, parent_id=folder_in.id
    )
    return folders


@router.get("/breadcrumbs/{folder_id}/", response_model=list[Breadcrumbs])
async def get_folder_breadcrumbs(
    session: SessionDep, folder_in: ValidatedFolder
) -> list[Breadcrumbs]:
    breadcrumbs = []
    current_folder = folder_in

    while current_folder and current_folder.parent_id is not None:
        breadcrumbs.append(
            Breadcrumbs(folder_id=current_folder.id, folder_name=current_folder.name)
        )
        current_folder = await storage_crud.get_folder_by_id(
            session=session, folder_id=current_folder.parent_id
        )

    breadcrumbs.reverse()

    return breadcrumbs


@router.get("/folder/root/", response_model=FolderPublic, responses=add_responses(404))
async def get_root_folder(
    session: SessionDep, current_user: CurrentUser
) -> FolderPublic:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(404, _("Root folder not found"))
    return root


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


@router.post("/{folder_id}/", response_model=str)
async def create_folder(session: SessionDep, folder_create: ValidatedNewFolder) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Folder created successfully")


@router.patch("/folder/{folder_id}/", response_model=str)
async def update_folder(
    session: SessionDep,
    folder_in: ValidatedFolder,
    new_name: Annotated[FolderUpdate, Form()],
) -> str:
    await storage_crud.update_folder(
        session=session, folder_in=folder_in, **new_name.model_dump()
    )
    return _("Folder renamed successfully")


@router.get("/suggested/folders/", response_model=list[FolderPublic])
async def get_suggested_folders(
    session: SessionDep, current_user: CurrentUser
) -> list[FolderPublic]:
    folders = await storage_crud.get_suggested_folders(
        session=session, user_id=current_user.id
    )
    return folders
