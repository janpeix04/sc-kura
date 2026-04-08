import uuid
from typing import Annotated

from fastapi import Depends, Form

from app.deps.auth import SessionDep, CurrentUser
from app.schemas.utils import error_codes, HTTPError
from app.i18n import _
from app.models import Folder
from app.crud import storage as storage_crud
from app.schemas.storage import NewFolder, FolderCreate


@error_codes(404)
async def validate_folder(session: SessionDep, folder_id: uuid.UUID) -> Folder:
    folder = await storage_crud.get_folder_by_id(session=session, folder_id=folder_id)
    if not folder:
        raise HTTPError(status_code=404, msg=_("Folder not found"))
    return folder


ValidatedFolder = Annotated[Folder, Depends(validate_folder)]


async def validate_new_folder(
    session: SessionDep,
    current_user: CurrentUser,
    folder_id: uuid.UUID,
    new_folder: Annotated[NewFolder, Form()],
) -> FolderCreate:
    parent_in = await validate_folder(session=session, folder_id=folder_id)
    count = await storage_crud.count_folder_with_name(
        session=session, name=new_folder.name, parent_id=parent_in.id
    )

    folder_name = new_folder.name

    if count > 0:
        folder_name = f"{folder_name} ({count})"

    path = "/"
    if parent_in.parent_id is not None and parent_in.path != "/":
        path = f"{parent_in.path}/{parent_in.name}"
    elif parent_in.parent_id is not None and parent_in.path == "/":
        path = f"/{parent_in.name}"

    return FolderCreate(
        name=folder_name,
        path=path,
        parent_id=parent_in.id,
        user_id=current_user.id,
    )


ValidatedNewFolder = Annotated[FolderCreate, Depends(validate_new_folder)]
