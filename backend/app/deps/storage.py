from typing import Annotated

from fastapi import Depends
from app.deps.auth import SessionDep

from app.schemas.uitls import error_codes, HTTPError
from app.models import Folder
from app.crud import storage as storage_crud


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


ValidatedPath = Annotated[str, Depends(validate_path)]
ValidatedParentFolder = Annotated[Folder, Depends(validate_parent_folder)]
