from typing import Annotated

from fastapi import Depends
from app.deps.auth import SessionDep, CurrentUser

from app.schemas.uitls import error_codes, HTTPError
from app.models import Folder
from app.crud import storage as storage_crud
from app.schemas.storage import FolderCreate


@error_codes(400)
def validate_path(path: str):
    if not isinstance(path, str):
        raise HTTPError(status_code=400, msg="Path must be an string")
    return str(path.replace("-", "/"))


@error_codes(404)
async def validate_parent_folder(session: SessionDep, path: str) -> Folder:
    path = validate_path(path)
    path = f"/{path}" if path != "/" else path
    folder = await storage_crud.get_folder_by_path(session=session, path=path)

    if not folder:
        raise HTTPError(status_code=404, msg="Parent folder not found")

    return folder


async def validate_folder_in(
    session: SessionDep, current_user: CurrentUser, folder_name: str, path: str
) -> FolderCreate:
    new_path = validate_path(path=path)
    print(new_path)
    new_path = "/" if new_path == "/" else f"/{new_path.strip('/')}"
    folder = await storage_crud.get_folder_by_name_and_path(
        session=session, folder_name=folder_name, path=new_path
    )

    if folder:
        raise HTTPError(
            status_code=409,
            msg=f"Folder with name {folder_name} already exists in {path}",
        )

    parent = await storage_crud.get_folder_by_path(session=session, path=new_path)
    if not parent:
        raise HTTPError(status_code=404, msg=f"Parent folder {new_path} not found")

    return FolderCreate(
        original_name=folder_name,
        stored_name=folder_name,
        path=f"{new_path}/{folder_name}" if new_path != "/" else f"/{folder_name}",
        user_id=current_user.id,
        parent_id=parent.id,
    )


ValidatedPath = Annotated[str, Depends(validate_path)]
ValidatedParentFolder = Annotated[Folder, Depends(validate_parent_folder)]
ValidatedFolderCreate = Annotated[FolderCreate, Depends(validate_folder_in)]
