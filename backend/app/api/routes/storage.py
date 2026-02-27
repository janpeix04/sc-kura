import io
import zipfile
from collections import defaultdict

from typing import List
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.api.file_services import FileSystemStorage, StorageFile, get_hard_diks_space
from app.deps.auth import SessionDep, CurrentUser
from app.crud import storage as storage_crud
from app.models import File as FileStorage, Folder
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
    FileFolderPublic,
    AvailableSpace,
    UploadFiles,
)

router = APIRouter(prefix="/storage", tags=["storage"])

fs = FileSystemStorage(settings.STORAGE_KURA_UPLOADS)


def to_public(entity: FileStorage | Folder) -> FileFolderPublic:
    if isinstance(entity, FileStorage):
        parent_id = entity.folder_id
    else:
        parent_id = entity.parent_id

    return FileFolderPublic(
        id=entity.id,
        name=entity.original_name,
        size=entity.size,
        path=entity.path,
        type=entity.mime_type,
        lastModified=entity.updated_at,
        parent_id=parent_id,
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


@router.post("/create/folder/{folder_name}/{path}/", response_model=str)
async def create_folder(session: SessionDep, folder_in: ValidatedFolderCreate) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_in)
    return "Folder created successfully!"


@router.get("/suggested/folders/", response_model=List[FileFolderPublic])
async def get_suggested_folders(
    session: SessionDep, current_user: CurrentUser
) -> List[FileFolderPublic]:
    folders = await storage_crud.get_suggested_folders(
        session=session, user_id=current_user.id
    )
    return [to_public(folder) for folder in folders]


@router.get("/suggested/files/", response_model=List[FileFolderPublic])
async def get_suggested_files(
    session: SessionDep, current_user: CurrentUser
) -> List[FileFolderPublic]:
    files = await storage_crud.get_suggested_files(
        session=session, user_id=current_user.id
    )
    return [to_public(file) for file in files]


@router.get("/root/", response_model=FileFolderPublic, responses=add_responses(404))
async def get_root(session: SessionDep, current_user: CurrentUser) -> FileFolderPublic:
    root = await storage_crud.get_root(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(status_code=404, msg="Root folder not found")
    return to_public(root)


@router.get("/items/{folder_id}/", response_model=List[FileFolderPublic])
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


async def _move_folders_to_trash_recursive(
    session: SessionDep, user_id: str, folder: Folder
):
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
        session=session, folder_id=folder.id, user_id=user_id
    )
    for subfolder in subfolders:
        await _move_folders_to_trash_recursive(
            session=session, user_id=user_id, folder=subfolder
        )


@router.patch("/move-to-trash/folder/{folder_id}/", response_model=str)
async def move_folder_to_trash(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    await _move_folders_to_trash_recursive(
        session=session, user_id=current_user.id, folder=folder_in
    )

    return "Folder moved to trash"


@router.patch("/move-to-trash/file/{file_id}/", response_model=str)
async def move_file_to_trash(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file_status(
        session=session, file=file_in, status=FileFolderStatus.DELETED
    )

    return "File moved to trash"


@router.patch("/rename/folder/{folder_id}/", response_model=str)
async def rename_folder(
    session: SessionDep, folder_in: ValidatedFolder, folder_name: str
) -> str:
    await storage_crud.rename_folder(
        session=session, folder=folder_in, new_folder_name=folder_name
    )
    return "Folder renamed successfully"


@router.patch("/rename/file/{file_id}/", response_model=str)
async def rename_file(
    session: SessionDep, file_in: ValidatedFile, file_name: str
) -> str:
    await storage_crud.rename_file(
        session=session, file=file_in, new_file_name=file_name
    )
    return "File renamed successfully"


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


async def collect_files_for_folder(
    session: SessionDep, user_id: str, folder: Folder, base_path: str | None = None
):
    """
    Recursively collect all files under a folder.
    Returns a list of tuples: (disk_path, zip_virtual_path)
    base_path: the path inside the zip (grows as we recurse)
    """
    collected = []

    if base_path is None:
        base_path = Path(folder.original_name)

    files = await storage_crud.get_files_in_folder(
        session=session, folder_id=folder.id, user_id=user_id
    )
    for file in files:
        disk_path = Path(file.path)
        zip_path = base_path / file.original_name
        collected.append((disk_path, zip_path))

    subfolders = await storage_crud.get_folders_in_folder(
        session=session, folder_id=folder.id, user_id=user_id
    )
    for subfolder in subfolders:
        collected += await collect_files_for_folder(
            session=session,
            user_id=user_id,
            folder=subfolder,
            base_path=base_path / subfolder.original_name,
        )

    return collected


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
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> StreamingResponse:
    files = await collect_files_for_folder(
        session=session, user_id=current_user.id, folder=folder_in
    )
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


@router.get("/delete/items/", response_model=List[FileFolderPublic])
async def get_deleted_items(
    session: SessionDep, current_user: CurrentUser
) -> List[FileFolderPublic]:
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

    def collect_descendant(folder: Folder):
        for child in children_map.get(folder.id, []):
            hidden_folder_ids.add(child.id)
            collect_descendant(child)

    for folder in top_level_folders:
        collect_descendant(folder)

    files = [file for file in deleted_files if file.folder_id not in deleted_folder_ids]
    return [to_public(item) for item in top_level_folders + files]


@router.patch("/restore/file/{file_id}/", response_model=str)
async def restore_file(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file_status(
        session=session, file=file_in, status=FileFolderStatus.UPLOADED
    )
    return "File restored successfully"


async def _restore_folders_recursive(session: SessionDep, user_id: str, folder: Folder):
    await storage_crud.update_folder_status(
        session=session, folder=folder, status=FileFolderStatus.UPLOADED
    )
    files = await storage_crud.get_files_in_folder(
        session=session,
        folder_id=folder.id,
        user_id=user_id,
        status=FileFolderStatus.DELETED,
    )
    if files:
        for file in files:
            await storage_crud.update_file_status(
                session=session, file=file, status=FileFolderStatus.UPLOADED
            )

    subfolders = await storage_crud.get_folders_in_folder(
        session=session,
        folder_id=folder.id,
        user_id=user_id,
        status=FileFolderStatus.DELETED,
    )
    for subfolder in subfolders:
        await _restore_folders_recursive(
            session=session, user_id=user_id, folder=subfolder
        )


@router.patch("/restore/folder/{folder_id}/", response_model=str)
async def restore_folder(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
):
    print("Folder root:", folder_in)
    await _restore_folders_recursive(
        session=session, user_id=current_user.id, folder=folder_in
    )
    return "Folder restored successfully"


@router.delete("/delete/file/{file_id}/", response_model=str)
async def delete_file_forever(session: SessionDep, file_in: ValidatedFile) -> str:
    storage_file = StorageFile(name=file_in.stored_name, storage=fs)
    if storage_file.exists():
        storage_file.delete()
    await storage_crud.delete_file(session=session, file=file_in)
    return "File deleted forever successfully"


@router.delete("/delete/folder/{folder_id}/", response_model=str)
async def delete_folder_forever(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    child_files: List[FileStorage] = []

    async def get_files_recursive(user_id: str, folder_id: str):
        files = await storage_crud.get_files_in_folder(
            session=session,
            folder_id=folder_id,
            user_id=user_id,
            status=FileFolderStatus.DELETED,
        )
        child_files.extend(files)
        subfolders = await storage_crud.get_folders_in_folder(
            session=session,
            folder_id=folder_id,
            user_id=user_id,
            status=FileFolderStatus.DELETED,
        )
        for subfolder in subfolders:
            await get_files_recursive(user_id=user_id, folder_id=subfolder.id)

    await get_files_recursive(user_id=current_user.id, folder_id=folder_in.id)
    for file in child_files:
        storage_file = StorageFile(name=file.stored_name, storage=fs)
        if storage_file.exists():
            storage_file.delete()

    await storage_crud.delete_folder(session=session, folder=folder_in)

    return "Folder deleted forever successfully"
