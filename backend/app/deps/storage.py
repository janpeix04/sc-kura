import uuid
from typing import Annotated

from fastapi import Depends

from app.deps.auth import SessionDep
from app.schemas.utils import error_codes, HTTPError
from app.i18n import _
from app.models import Folder
from app.crud import storage as storage_crud


@error_codes(404)
async def validate_folder(session: SessionDep, folder_id: uuid.UUID) -> Folder:
    folder = await storage_crud.get_folder_by_id(session=session, folder_id=folder_id)
    if not folder:
        raise HTTPError(status_code=404, msg=_("Folder not found"))
    return folder


ValidatedFolder = Annotated[Folder, Depends(validate_folder)]
