from typing import List
from fastapi import APIRouter, UploadFile, File

from app.core.config import settings
from app.api.file_services import (
    FileSystemStorage,
    StorageFile,
)
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.deps.storage import ValidatedPath, ValidatedParentFolder
from app.schemas.storage import FileCreate, FileStatus, FileFolderPublic

router = APIRouter(prefix="/storage", tags=["storage"])

fs = FileSystemStorage(settings.STORAGE_KURA_UPLOADS)


@router.get("/files/{path}/", response_model=List[FileFolderPublic])
async def get_files(
    session: SessionDep, current_user: CurrentUser, parent_folder: ValidatedParentFolder
) -> List[FileFolderPublic]:
    files = await storage_crud.get_files_by_folder_id(
        session=session, folder_id=parent_folder.id, user_id=current_user.id
    )
    return [
        FileFolderPublic(
            id=file.id,
            name=file.original_name,
            size=file.size,
            path=file.path,
            type=file.mime_type,
            lastModified=file.updated_at,
        )
        for file in files
    ]


@router.get("/folders/{path}/", response_model=List[FileFolderPublic])
async def get_folders(
    session: SessionDep, current_user: CurrentUser, parent_folder: ValidatedParentFolder
) -> List[FileFolderPublic]:
    folders = await storage_crud.get_folders_by_folder_id(
        session=session, folder_id=parent_folder.id, user_id=current_user.id
    )
    return [
        FileFolderPublic(
            id=folder.id,
            name=folder.original_name,
            size=folder.size,
            path=folder.path,
            type=folder.mime_type,
            lastModified=folder.updated_at,
        )
        for folder in folders
    ]


@router.post("/upload/multiple/{path}/", response_model=str)
async def upload_multiple(
    session: SessionDep,
    current_path: ValidatedPath,
    current_user: CurrentUser,
    files: List[UploadFile] = File(...),
) -> str:
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
        await storage_crud.create_file(
            session=session, file_create=file_create, folder_id=folder.id
        )
        await storage_crud.update_folder_size_recursive(
            session=session, folder=folder, size=file.size
        )

    return f"Uploaded {len(files)} file(s) successfully!"
