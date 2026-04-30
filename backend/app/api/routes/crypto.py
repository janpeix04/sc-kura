from typing import Annotated

from fastapi import APIRouter, Form

from app.crud import crypto as crypto_crud
from app.deps.auth import SessionDep, CurrentUser
from app.deps.crypto import ValidatedEncryptedFolder, ValidatedNewEncryptedFolder
from app.i18n import _
from app.schemas.crypto import (
    EncryptedFolderCreate,
    EncryptedFolderPublic,
    EncryptedFolderRename,
)
from app.schemas.users import UserKeyCreate, UserKeyPublic
from app.schemas.utils import HTTPError, add_responses
from app.schemas.storage import FolderStatus

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.post("/user/keys/", response_model=UserKeyPublic)
async def save_user_keys(
    session: SessionDep,
    keys: Annotated[UserKeyCreate, Form()],
) -> UserKeyPublic:
    user_keys = await crypto_crud.create_user_key(session=session, keys_create=keys)
    return user_keys


@router.get("/users/keys/", response_model=UserKeyPublic, responses=add_responses(404))
async def get_user_keys(
    session: SessionDep, current_user: CurrentUser
) -> UserKeyPublic:
    keys = await crypto_crud.get_user_key(session=session, user_id=current_user.id)
    if keys is None:
        raise HTTPError(status_code=404, msg=_("No keys found for this user"))
    return keys


@router.post("/root/", response_model=str)
async def create_root(session: SessionDep, current_user: CurrentUser) -> str:
    folder_create = EncryptedFolderCreate(
        encrypted_key="/", iv="/", encrypted_name="/", user_id=current_user.id
    )
    await crypto_crud.create_folder(session=session, folder_create=folder_create)
    return _("Root folder created successfully")


@router.get("/root/", response_model=EncryptedFolderPublic)
async def get_root(
    session: SessionDep, current_user: CurrentUser
) -> EncryptedFolderPublic:
    root = await crypto_crud.get_root(session=session, user_id=current_user.id)
    if root is None:
        raise HTTPError(status_code=404, msg=_("Root folder not found"))
    return root


@router.post("/folder/{folder_id}/", response_model=str)
async def create_folder(
    session: SessionDep,
    folder_create: ValidatedNewEncryptedFolder,
) -> str:
    await crypto_crud.create_folder(session=session, folder_create=folder_create)
    return _("Folder created successfully")


@router.get("/folders/{folder_id}/", response_model=list[EncryptedFolderPublic])
async def get_folders_in_folder(
    session: SessionDep,
    parent_in: ValidatedEncryptedFolder,
    status: FolderStatus | None = None,
) -> list[EncryptedFolderPublic]:
    folders = await crypto_crud.get_folders_in_folder(
        session=session, parent_id=parent_in.id, status=status
    )
    return folders


@router.patch(
    "/rename/folder/{folder_id}/", response_model=str, responses=add_responses(400)
)
async def rename_folder(
    session: SessionDep,
    folder_in: ValidatedEncryptedFolder,
    payload: Annotated[EncryptedFolderRename, Form()],
) -> str:
    if payload.encrypted_name is None:
        raise HTTPError(status_code=400, msg=_("Please provide a valid folder name"))
    await crypto_crud.rename_folder(
        session=session, folder_in=folder_in, payload=payload
    )
    return _("Folder renamed successfully")
