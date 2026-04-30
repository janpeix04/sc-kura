import uuid
from typing import Annotated

from fastapi import Depends, Form

from app.deps.auth import SessionDep, CurrentUser
from app.crud import crypto as crypto_crud
from app.i18n import _
from app.models import EncryptedFolder
from app.schemas.crypto import NewEncryptedFolder, EncryptedFolderCreate
from app.schemas.utils import HTTPError, error_codes


@error_codes(404)
async def validate_folder(session: SessionDep, folder_id: uuid.UUID) -> EncryptedFolder:
    folder = await crypto_crud.get_folder_by_id(session=session, folder_id=folder_id)
    if not folder:
        raise HTTPError(status_code=404, msg=_("Folder not found"))
    return folder


ValidatedEncryptedFolder = Annotated[EncryptedFolder, Depends(validate_folder)]


async def validate_new_encrypted_folder(
    session: SessionDep,
    current_user: CurrentUser,
    folder_id: uuid.UUID,
    new_folder: Annotated[NewEncryptedFolder, Form()],
) -> EncryptedFolderCreate:
    parent = await validate_folder(session=session, folder_id=folder_id)
    return EncryptedFolderCreate(
        encrypted_key=new_folder.encrypted_key,
        iv=new_folder.iv,
        encrypted_name=new_folder.encrypted_name,
        parent_id=parent.id,
        user_id=current_user.id,
    )


ValidatedNewEncryptedFolder = Annotated[
    EncryptedFolderCreate, Depends(validate_new_encrypted_folder)
]
