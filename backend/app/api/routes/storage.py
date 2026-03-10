import io
import zipfile
from collections import defaultdict
import uuid

from typing import List
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.api.file_services import FileSystemStorage, StorageFile, get_hard_diks_space
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.models import Folder
from app.schemas.utils import HTTPError, add_responses
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
    FolderPublic,
    FileFolderPublic,
    AvailableSpace,
    UploadFiles,
)

from app.services.storage import (
    to_public_file,
    to_public_folder,
    collect_files_for_folder,
    move_folders_to_trash_recursive,
    restore_folders_recursive,
)

router = APIRouter(prefix="/storage", tags=["storage"])

fs = FileSystemStorage(settings.STORAGE_KURA_UPLOADS)


# --------------------------------------------------
# Available space + Root
# --------------------------------------------------


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


@router.get("/root/", response_model=FolderPublic, responses=add_responses(404))
async def get_root(session: SessionDep, current_user: CurrentUser) -> FolderPublic:
    root = await storage_crud.get_root(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(status_code=404, msg="Root folder not found")
    return to_public_folder(root)


# --------------------------------------------------
# Items (list folders/files)
# --------------------------------------------------


@router.get("/items/{folder_id}/", response_model=FileFolderPublic)
async def get_items(
    session: SessionDep,
    parent_folder: ValidatedParentFolder,
    status: FileFolderStatus = FileFolderStatus.UPLOADED,
) -> FileFolderPublic:
    folders = await storage_crud.get_folders_in_folder(
        session=session,
        folder_id=parent_folder.id,
        status=status,
    )
    files = await storage_crud.get_files_in_folder(
        session=session,
        folder_id=parent_folder.id,
        status=status,
    )
    return FileFolderPublic(
        folders=[to_public_folder(folder) for folder in folders],
        files=[
            to_public_file(
                file,
                folder_path=(
                    await storage_crud.get_folder_path_by_id(
                        session=session, folder_id=file.folder_id
                    )
                ),
            )
            for file in files
        ],
    )


@router.get("/delete/items/", response_model=FileFolderPublic)
async def get_deleted_items(
    session: SessionDep, current_user: CurrentUser
) -> FileFolderPublic:
    deleted_folders = await storage_crud.get_all_folders(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )
    deleted_files = await storage_crud.get_all_files(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )

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

    def collect_descendant(folder: Folder):
        for child in children_map.get(folder.id, []):
            hidden_folder_ids.add(child.id)
            collect_descendant(child)

    for folder in top_level_folders:
        collect_descendant(folder)

    files = [file for file in deleted_files if file.folder_id not in deleted_folder_ids]
    return FileFolderPublic(
        folders=[to_public_folder(folder) for folder in top_level_folders],
        files=[to_public_file(file) for file in files],
    )


# --------------------------------------------------
# Upload / Create
# --------------------------------------------------


@router.post("/create/folder/{folder_name}/{path}/", response_model=str)
async def create_folder(session: SessionDep, folder_in: ValidatedFolderCreate) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_in)
    return "Folder created successfully!"


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


# --------------------------------------------------
# Rename
# --------------------------------------------------


@router.patch("/rename/file/{file_id}/", response_model=str)
async def rename_file(
    session: SessionDep, file_in: ValidatedFile, file_name: str
) -> str:
    await storage_crud.update_file(
        session=session, file=file_in, original_name=file_name
    )
    return "File renamed successfully"


@router.patch("/rename/folder/{folder_id}/", response_model=str)
async def rename_folder(
    session: SessionDep, folder_in: ValidatedFolder, folder_name: str
) -> str:
    await storage_crud.update_folder(
        session=session, folder=folder_in, original_name=folder_name
    )
    return "Folder renamed successfully"


# --------------------------------------------------
# Trash (move to trash)
# --------------------------------------------------


@router.patch("/move-to-trash/file/{file_id}/", response_model=str)
async def move_file_to_trash(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file(
        session=session,
        file=file_in,
        status=FileFolderStatus.DELETED,
        original_folder_id=file_in.folder_id,
    )
    return "File moved to trash"


@router.patch("/move-to-trash/folder/{folder_id}/", response_model=str)
async def move_folder_to_trash(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    await move_folders_to_trash_recursive(
        session=session, user_id=current_user.id, folder=folder_in
    )

    return "Folder moved to trash"


# --------------------------------------------------
# Restore
# --------------------------------------------------


@router.patch("/restore/file/{file_id}/", response_model=str)
async def restore_file(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file(
        session=session, file=file_in, status=FileFolderStatus.UPLOADED
    )

    async def update_file_folder_id(folder_id: uuid.UUID):
        folder = await storage_crud.get_folder_by_id(
            session=session, folder_id=folder_id
        )
        if folder and folder.status == FileFolderStatus.UPLOADED:
            await storage_crud.update_file(
                session=session, file=file_in, folder_id=folder.id
            )
            return
        await update_file_folder_id(folder.parent_id)

    await update_file_folder_id(file_in.folder_id)

    return "File restored successfully"


@router.patch("/restore/folder/{folder_id}/", response_model=str)
async def restore_folder(session: SessionDep, folder_in: ValidatedFolder):
    await restore_folders_recursive(session=session, folder=folder_in)
    return "Folder restored successfully"


# --------------------------------------------------
# Permanent deletion
# --------------------------------------------------


@router.delete("/delete/file/{file_id}/", response_model=str)
async def delete_file_forever(session: SessionDep, file_in: ValidatedFile) -> str:
    storage_file = StorageFile(name=file_in.stored_name, storage=fs)
    if storage_file.exists():
        storage_file.delete()

    folder = await storage_crud.get_folder_by_id(
        session=session, folder_id=file_in.folder_id
    )
    if folder:
        await storage_crud.update_folder_size_recursive(
            session=session, folder=folder, size=-file_in.size
        )
    await storage_crud.delete_file(session=session, file=file_in)
    return "File deleted forever successfully"


@router.delete("/delete/folder/{folder_id}/", response_model=str)
async def delete_folder_forever(session: SessionDep, folder_in: ValidatedFolder) -> str:
    async def delete_tree(folder_id: uuid.UUID):
        restored_folders = await storage_crud.get_restored_folders_by_parent_id(
            session=session, parent_id=folder_id
        )
        for restored_folder in restored_folders:
            await storage_crud.update_folder(
                session=session, folder=restored_folder, original_parent_id=None
            )
        restored_files = await storage_crud.get_restored_files_by_folder_id(
            session=session, folder_id=folder_id
        )
        for restored_file in restored_files:
            await storage_crud.update_file(
                session=session, file=restored_file, original_folder_id=None
            )

        files = await storage_crud.get_files_in_folder(
            session=session,
            folder_id=folder_id,
            status=FileFolderStatus.DELETED,
        )
        for file in files:
            storage_file = StorageFile(name=file.stored_name, storage=fs)
            if storage_file.exists():
                storage_file.delete()

        subfolders = await storage_crud.get_folders_in_folder(
            session=session,
            folder_id=folder_id,
            status=FileFolderStatus.DELETED,
        )
        for subfolder in subfolders:
            await delete_tree(folder_id=subfolder.id)

    await delete_tree(folder_id=folder_in.id)
    await storage_crud.delete_folder(session=session, folder=folder_in)
    return "Folder deleted forever successfully"


@router.delete("/delete/all/", response_model=str)
async def delete_all(session: SessionDep, current_user: CurrentUser):
    restored_folders = await storage_crud.get_all_restored_folders(
        session=session, user_id=current_user.id
    )
    for restored_folder in restored_folders:
        await storage_crud.update_folder(
            session=session, folder=restored_folder, original_parent_id=None
        )

    restored_files = await storage_crud.get_all_restored_files(
        session=session, user_id=current_user.id
    )
    for restored_file in restored_files:
        await storage_crud.update_file(
            session=session, file=restored_file, original_folder_id=None
        )

    folders = await storage_crud.get_all_folders(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )
    folder_ids = {folder.id for folder in folders}
    files = await storage_crud.get_all_files(
        session=session, user_id=current_user.id, status=FileFolderStatus.DELETED
    )
    for file in files:
        storage_file = StorageFile(name=file.stored_name, storage=fs)
        if storage_file.exists():
            storage_file.delete()

    for folder in folders:
        await storage_crud.delete_folder(session=session, folder=folder)

    for file in files:
        if file.folder_id not in folder_ids:
            await storage_crud.delete_file(session=session, file=file)
    return "Trash emptied successfully"


# --------------------------------------------------
# Suggested items
# --------------------------------------------------


@router.get("/suggested/items/", response_model=FileFolderPublic)
async def get_suggested_items(
    session: SessionDep, current_user: CurrentUser
) -> FileFolderPublic:
    folders = await storage_crud.get_suggested_folders(
        session=session, user_id=current_user.id
    )
    files = await storage_crud.get_suggested_files(
        session=session, user_id=current_user.id
    )
    return FileFolderPublic(
        folders=[to_public_folder(folder) for folder in folders],
        files=[to_public_file(file) for file in files],
    )


# --------------------------------------------------
# Download File/Folder
# --------------------------------------------------


@router.get(
    "/download/file/{file_id}/",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "File download",
        }
    },
)
async def download_file(file_in: ValidatedFile):
    file_path = Path(file_in.path)
    if not file_path.exists():
        raise HTTPError(status_code=404, msg="File not found")
    return FileResponse(
        path=file_path, filename=file_in.original_name, media_type=file_in.mime_type
    )


@router.get(
    "/download/folder/{folder_id}/",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": "ZIP archive of the folder",
        }
    },
)
async def download_folder(
    session: SessionDep, folder_in: ValidatedFolder
) -> StreamingResponse:
    files = await collect_files_for_folder(session=session, folder=folder_in)
    if not files:
        raise HTTPError(status_code=404, msg="Folder is empty")
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        for disk_path, zip_path in files:
            if disk_path.exists():
                zf.write(disk_path, arcname=zip_path)
    zip_io.seek(0)
    return StreamingResponse(
        zip_io,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={folder_in.original_name}.zip"
        },
    )
