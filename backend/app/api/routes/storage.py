from typing import List

from fastapi import APIRouter, UploadFile, File

from app.core.config import settings
from app.api.file_services import (
    FileSystemStorage,
    StorageFile,
)
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.deps.storage import ValidatedPath
from app.schemas.storage import FileCreate, FileStatus

router = APIRouter(prefix="/storage", tags=["storage"])

fs = FileSystemStorage(settings.STORAGE_KURA_UPLOADS)


@router.post("/upload/multiple/{path}/")
async def upload_multiple(
    session: SessionDep,
    current_path: ValidatedPath,
    current_user: CurrentUser,
    files: List[UploadFile] = File(...),
):
    for file in files:
        folder = await storage_crud.ensure_folder_tree(
            session=session,
            base_path=current_path,
            file_path=file.filename,
            user_id=current_user.id,
        )

        storage = StorageFile(name=file.filename, storage=fs)
        storage.write(file=file.file, user_id=current_user.id)

        file_create = FileCreate(
            original_name=file.filename.split("/")[-1],
            stored_name=storage.name,
            path=storage.path,
            size=file.size,
            mime_type=file.content_type,
            status=FileStatus.UPLOADED,
            user_id=current_user.id,
            folder_id=folder.id,
        )
        await storage_crud.create_file(session=session, file_create=file_create)

    return {"files_received": files}
