from typing import Annotated

from fastapi import APIRouter, Form, UploadFile

from app.core.config import settings
from app.crud import storage as storage_crud
from app.deps.auth import SessionDep, CurrentUser
from app.deps.storage import ValidatedFile, ValidatedFolder, ValidatedNewFolder
from app.i18n import _
from app.schemas.storage import (
    FileCreate,
    FolderPublic,
    FolderCreate,
    FolderUpdate,
    Breadcrumbs,
    FilePublic,
    FileStatus,
)
from app.schemas.utils import HTTPError, add_responses
from app.services.filesystem import FileSystemStorage, StorageFile

router = APIRouter(prefix="/storage", tags=["storage"])

fs_upload = FileSystemStorage(settings.STORAGE_UPLOADS)
fs_chunk = FileSystemStorage(settings.STORAGE_CHUNK)


@router.get("/folders/{folder_id}/", response_model=list[FolderPublic])
async def get_folders_in_folder(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> list[FolderPublic]:
    folders = await storage_crud.get_folders_in_folders(
        session=session, parent_id=folder_in.id
    )
    return folders


@router.get("/breadcrumbs/{folder_id}/", response_model=list[Breadcrumbs])
async def get_folder_breadcrumbs(
    session: SessionDep, folder_in: ValidatedFolder
) -> list[Breadcrumbs]:
    breadcrumbs = []
    current_folder = folder_in

    while current_folder and current_folder.parent_id is not None:
        breadcrumbs.append(
            Breadcrumbs(folder_id=current_folder.id, folder_name=current_folder.name)
        )
        current_folder = await storage_crud.get_folder_by_id(
            session=session, folder_id=current_folder.parent_id
        )

    breadcrumbs.reverse()

    return breadcrumbs


@router.get("/folder/root/", response_model=FolderPublic, responses=add_responses(404))
async def get_root_folder(
    session: SessionDep, current_user: CurrentUser
) -> FolderPublic:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    if not root:
        raise HTTPError(404, _("Root folder not found"))
    return root


@router.post("/folder/root/", response_model=str)
async def create_root_folder(session: SessionDep, current_user: CurrentUser) -> str:
    folder_create = FolderCreate(
        name="/",
        path="/",
        owner=f"{current_user.first_name} {current_user.last_name}",
        user_id=current_user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Root folder created successfully")


@router.post("/{folder_id}/", response_model=str)
async def create_folder(session: SessionDep, folder_create: ValidatedNewFolder) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Folder created successfully")


@router.patch("/folder/{folder_id}/", response_model=str)
async def update_folder(
    session: SessionDep,
    folder_in: ValidatedFolder,
    new_name: Annotated[FolderUpdate, Form()],
) -> str:
    await storage_crud.update_folder(
        session=session, folder_in=folder_in, **new_name.model_dump()
    )
    return _("Folder renamed successfully")


@router.get("/suggested/folders/", response_model=list[FolderPublic])
async def get_suggested_folders(
    session: SessionDep, current_user: CurrentUser
) -> list[FolderPublic]:
    folders = await storage_crud.get_suggested_folders(
        session=session, user_id=current_user.id
    )
    return folders


@router.get("/suggested/files/", response_model=list[FolderPublic])
async def get_suggested_files(
    session: SessionDep, current_user: CurrentUser
) -> list[FilePublic]:
    files = await storage_crud.get_suggested_files(
        session=session, user_id=current_user.id
    )
    return files


@router.get("/files/{folder_id}/", response_model=list[FilePublic])
async def get_files_in_folder(
    session: SessionDep, folder_in: ValidatedFolder
) -> list[FilePublic]:
    files = await storage_crud.get_files_in_folder(
        session=session, folder_id=folder_in.id
    )
    return files


@router.post("/upload/{folder_id}/", response_model=str)
async def upload_file(
    session: SessionDep,
    current_user: CurrentUser,
    folder_in: ValidatedFolder,
    file: UploadFile,
) -> str:
    storage = StorageFile(name=file.filename, storage=fs_upload)
    path = storage.write(file.file, user_id=current_user.id, folder_id=folder_in.id)

    file_create = FileCreate(
        name=file.filename,
        stored_name=storage.name,
        location=folder_in.name,
        path=path,
        type=storage.mime_type,
        size=storage.size,
        owner=f"{current_user.first_name} {current_user.last_name}",
        user_id=current_user.id,
        parent_id=folder_in.id,
    )
    file = await storage_crud.create_file(session=session, file_create=file_create)

    return _("File uploaded successfully")


@router.delete("/file/{file_id}/", response_model=str)
async def delete_file(session: SessionDep, file_in: ValidatedFile) -> str:
    storage = StorageFile(name=file_in.stored_name, storage=fs_upload)
    if storage.exists():
        storage.delete()

    await storage_crud.delete_file(session=session, file=file_in)
    return _("File deleted successfully")


@router.patch("/move-to-trash/file/{file_id}/", response_model=str)
async def move_file_to_trash(session: SessionDep, file_in: ValidatedFile) -> str:
    await storage_crud.update_file(
        session=session,
        file=file_in,
        **{"status": FileStatus.DELETED},
    )
    return _("File move to trash")
