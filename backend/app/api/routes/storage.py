from typing import List
from fastapi import APIRouter, UploadFile, File
from collections import defaultdict

from app.core.config import settings
from app.api.file_services import FileSystemStorage, StorageFile, get_hard_diks_space
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.models import File as FileStorage, Folder
from app.deps.storage import (
    ValidatedPath,
    ValidatedParentFolder,
    ValidatedFolderCreate,
    ValidatedFolder,
    ValidatedFile,
)
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
    used_space = await storage_crud.get_user_storage_used(
        session=session, user_id=current_user.id
    )
    total_space = get_hard_diks_space()
    free_space = total_space - used_space
    return AvailableSpace(total=total_space, used=used_space, free=free_space)


@router.get("/items/{path}/", response_model=List[FileFolderPublic])
async def get_items(
    session: SessionDep,
    current_user: CurrentUser,
    parent_folder: ValidatedParentFolder,
    status: FileFolderStatus = FileFolderStatus.UPLOADED,
) -> List[FileFolderPublic]:
    folders = await storage_crud.get_folders_in_folder(
        session=session,
        folder_id=parent_folder.id,
        user_id=current_user.id,
        status=status,
    )
    files = await storage_crud.get_files_in_folder(
        session=session,
        folder_id=parent_folder.id,
        user_id=current_user.id,
        status=status,
    )
    return [to_public(item) for item in folders + files]


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
            existing = await storage_crud.get_file_in_folder(
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


async def _move_folders_to_recycle_recursive(
    *, session: SessionDep, user_id: str, folder: Folder
) -> None:
    await storage_crud.update_folder_status(
        session=session, folder=folder, status=FileFolderStatus.DELETED
    )

    files = await storage_crud.get_files_in_folder(
        session=session, folder_id=folder.id, user_id=user_id
    )
    if files:
        for file in files:
            await storage_crud.update_file_status(
                session=session, file=file, status=FileFolderStatus.DELETED
            )

    subfolders = await storage_crud.get_folders_in_folder(
        session=session,
        folder_id=folder.id,
        user_id=user_id,
        status=FileFolderStatus.UPLOADED,
    )
    for subfolder in subfolders:
        await _move_folders_to_recycle_recursive(
            session=session, user_id=user_id, folder=subfolder
        )


@router.post("/move-to-recycle/folder/{folder_id}/", response_model=str)
async def delete_folder(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    await _move_folders_to_recycle_recursive(
        session=session, user_id=current_user.id, folder=folder_in
    )
    return "Folder move to Recycle Bin successfully!"


@router.post("/move-to-recycle/file/{file_id}/", response_model=str)
async def delete_file(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file_status(
        session=session, file=file_in, status=FileFolderStatus.DELETED
    )
    return "Folder move to Recycle Bin successfully!"


@router.get("/deleted/items/{path}/", response_model=List[FileFolderPublic])
async def get_deleted_items(
    session: SessionDep, current_user: CurrentUser, path: ValidatedPath
) -> List[FileFolderPublic]:
    if path != "/":
        folder = await storage_crud.get_folder_by_path(
            session=session,
            path=path,
            user_id=current_user.id,
            status=FileFolderStatus.DELETED,
        )
        folders = await storage_crud.get_folders_in_folder(
            session=session,
            user_id=current_user.id,
            folder_id=folder.id,
            status=FileFolderStatus.DELETED,
        )
        files = await storage_crud.get_files_in_folder(
            session=session,
            folder_id=folder.id,
            user_id=current_user.id,
            status=FileFolderStatus.DELETED,
        )
        return [to_public(item) for item in folders + files]

    deleted_folders = await storage_crud.get_all_folders(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )
    deleted_files = await storage_crud.get_all_files(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )

    if not deleted_files and deleted_folders:
        return []

    children_map = defaultdict(list)
    for folder in deleted_folders:
        children_map[folder.parent_id].append(folder)
    deleted_folder_ids = {folder.id for folder in deleted_folders}

    top_level_folders = [
        folder
        for folder in deleted_folders
        if folder.parent_id not in deleted_folder_ids
    ]

    hidden_folder_ids = set()

    def collect_descendants(folder: Folder):
        for child in children_map.get(folder.id, []):
            hidden_folder_ids.add(child.id)
            collect_descendants(child)

    for folder in top_level_folders:
        collect_descendants(folder)

    files = [file for file in deleted_files if file.folder_id not in deleted_folder_ids]

    return [to_public(item) for item in top_level_folders + files]
