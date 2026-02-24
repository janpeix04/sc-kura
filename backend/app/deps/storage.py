from typing import Annotated

from fastapi import Depends
from app.deps.auth import SessionDep, CurrentUser

from app.schemas.utils import error_codes, HTTPError
from app.models import Folder, File
from app.crud import storage as storage_crud
from app.schemas.storage import FolderCreate, FileFolderStatus


@error_codes(400)
def validate_path(path: str):
    normalized = path.replace("-", "/")
    return "/" if normalized == "/" else f"/{normalized.strip('/')}"


@error_codes(404)
async def validate_parent_folder(
    session: SessionDep, current_user: CurrentUser, path: str
) -> Folder:
    path = validate_path(path)
    folder = await storage_crud.get_folder_by_path(
        session=session, path=path, user_id=current_user.id
    )

    if not folder:
        raise HTTPError(status_code=404, msg="Parent folder not found")

    return folder


@error_codes(409)
async def validate_folder_in_path(
    session: SessionDep, current_user: CurrentUser, folder_name: str, path: str
) -> FolderCreate:
    new_path = validate_path(path=path)
    new_folder_path = (
        f"{new_path}/{folder_name}" if new_path != "/" else f"/{folder_name}"
    )
    folder = await storage_crud.get_folder_in_path(
        session=session,
        folder_name=folder_name,
        path=new_folder_path,
        user_id=current_user.id,
    )
    if folder:
        raise HTTPError(
            status_code=409,
            msg=f"Folder with name {folder_name} already exists in {new_path}",
        )

    parent = await storage_crud.get_folder_by_path(
        session=session, path=new_path, user_id=current_user.id
    )
    if not parent:
        raise HTTPError(status_code=404, msg=f"Parent folder {new_path} not found")

    return FolderCreate(
        original_name=folder_name,
        stored_name=folder_name,
        path=new_folder_path,
        status=FileFolderStatus.UPLOADED,
        user_id=current_user.id,
        parent_id=parent.id,
    )


@error_codes(404)
async def validate_folder_in(
    session: SessionDep, folder_id: str, current_user: CurrentUser
) -> Folder:
    folder = await storage_crud.get_folder_by_folder_id(
        session=session, folder_id=folder_id, user_id=current_user.id
    )
    if not folder:
        raise HTTPError(status_code=404, msg="Folder not found")
    return folder


@error_codes(404)
async def validate_file_in(session: SessionDep, file_id: str) -> Folder:
    file = await storage_crud.get_file_by_file_id(session=session, file_id=file_id)
    if not file:
        raise HTTPError(status_code=404, msg="File not found")
    return file


ValidatedPath = Annotated[str, Depends(validate_path)]
ValidatedParentFolder = Annotated[Folder, Depends(validate_parent_folder)]
ValidatedFolderCreate = Annotated[FolderCreate, Depends(validate_folder_in_path)]
ValidatedFolder = Annotated[Folder, Depends(validate_folder_in)]
ValidatedFile = Annotated[File, Depends(validate_file_in)]
