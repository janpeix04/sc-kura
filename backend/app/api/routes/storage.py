from typing import List
from fastapi import APIRouter, UploadFile, File

from app.core.config import settings
from app.api.file_services import FileSystemStorage, StorageFile, get_hard_diks_space
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.models import File as FileStorage, Folder
from app.deps.storage import ValidatedPath, ValidatedParentFolder, ValidatedFolderCreate
from app.schemas.storage import (
    FileCreate,
    FileFolderStatus,
    FileFolderPublic,
    AvailableSpace,
    UploadFiles,
)

router = APIRouter(prefix="/storage", tags=["storage"])

fs = FileSystemStorage(settings.STORAGE_KURA_UPLOADS)


def to_public(entity: FileStorage | Folder) -> FileFolderPublic:
    return FileFolderPublic(
        id=entity.id,
        name=entity.original_name,
        size=entity.size,
        path=entity.path,
        type=entity.mime_type,
        lastModified=entity.updated_at,
    )


@router.get("/available/space/", response_model=AvailableSpace)
async def get_available_space(
    session: SessionDep, current_user: CurrentUser
) -> AvailableSpace:
    used_space = await storage_crud.get_total_file_size(
        session=session, user_id=current_user.id
    )
    total_space = get_hard_diks_space()
    free_space = total_space - used_space
    return AvailableSpace(total=total_space, used=used_space, free=free_space)


""" @router.get("/items/{path}/")
async def get_items(session: SessionDep, current_user: CurrentUser, parent_folder: ValidatedParentFolder) """


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


@router.post("/upload/multiple/{path}/", response_model=UploadFiles)
async def upload_multiple(
    session: SessionDep,
    current_path: ValidatedPath,
    current_user: CurrentUser,
    files: List[UploadFile] = File(...),
) -> str:
    uploaded = []
    errors = []

    for file in files:
        try:
            folder = await storage_crud.ensure_folder_tree(
                session=session,
                base_path=current_path,
                file_path=file.filename,
                user_id=current_user.id,
            )

            file_name = file.filename.split("/")[-1]
            existing = await storage_crud.get_file_by_path_and_folder_id(
                session=session,
                file_name=file_name,
                folder_id=folder.id,
                user_id=current_user.id,
            )
            if existing:
                errors.append(f"{file_name} already exists")
                continue

            storage = StorageFile(name=file.filename, storage=fs)
            storage.write(file=file.file, user_id=current_user.id)

            file_create = FileCreate(
                original_name=file.filename.split("/")[-1],
                stored_name=storage.name,
                path=storage.path,
                size=file.size,
                mime_type=file.content_type,
                status=FileFolderStatus.UPLOADED,
                user_id=current_user.id,
                folder_id=folder.id,
            )
            await storage_crud.create_file(session=session, file_create=file_create)
            await storage_crud.update_folder_size_recursive(
                session=session, folder=folder, size=file.size
            )
            uploaded.append(file_name)
        except Exception as e:
            errors.append(f"{file_name}: {str(e)}")

    return UploadFiles(
        uploaded=uploaded,
        errors=errors,
        total_uploaded=len(uploaded),
        total_errors=len(errors),
    )


@router.post("/create/folder/{folder_name}/{path}/", response_model=str)
async def create_folder(session: SessionDep, folder_in: ValidatedFolderCreate) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_in)
    return "Folder created successfully!"
