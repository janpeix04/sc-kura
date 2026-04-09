import uuid
from typing import Annotated

from fastapi import APIRouter, Form, UploadFile

from app.crud import storage as storage_crud
from app.core.config import settings
from app.deps.auth import SessionDep, CurrentUser
from app.deps.storage import ValidatedFolder, ValidatedNewFolder
from app.i18n import _
from app.services.filesystem import FileSystemStorage, StorageFile
from app.schemas.storage import (
    FolderPublic,
    FolderCreate,
    FolderUpdate,
    Breadcrumbs,
    FileCreate,
    FileUploadChunkComplete,
)
from app.schemas.utils import HTTPError, add_responses

router = APIRouter(prefix="/storage", tags=["storage"])

fs_upload = FileSystemStorage(settings.STORAGE_UPLOADS)
fs_chunk = FileSystemStorage(settings.STORAGE_CHUNK)


@router.get("/folders/{folder_id}/", response_model=list[FolderPublic])
async def get_folders_in_folder(
    session: SessionDep, folder_in: ValidatedFolder
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


@router.post("/upload/file/{folder_id}/", response_model=str)
async def upload_file(
    session: SessionDep,
    current_user: CurrentUser,
    folder_in: ValidatedFolder,
    file: UploadFile,
) -> str:
    storage = StorageFile(name=file.filename, storage=fs_upload)
    path = storage.write(
        file=file.file, user_id=current_user.id, folder_id=folder_in.id
    )
    size = fs_upload.get_size(storage.name)

    file_create = FileCreate(
        name=file.filename,
        location=folder_in.name,
        path=path,
        type=file.content_type,
        size=size,
        owner=f"{current_user.first_name} {current_user.last_name}",
        folder_id=folder_in.id,
        user_id=current_user.id,
    )
    file = await storage_crud.create_file(session=session, file_create=file_create)

    return _("File upload successfully")


@router.post("/upload/chunk/", response_model=str)
async def upload_chunk(
    chunk: UploadFile,
    upload_id: uuid.UUID = Form(),
    index: int = Form(),
) -> str:
    chunk_name = f"{upload_id}_{index}"

    storage = StorageFile(name=chunk_name, storage=fs_chunk)
    storage.write(chunk.file)

    return _("Chunk received")


@router.post(
    "/upload/complete/{folder_id}/", response_model=str, responses=add_responses(400)
)
async def complete_upload(
    session: SessionDep,
    current_user: CurrentUser,
    chunk_meta: Annotated[FileUploadChunkComplete, Form()],
    folder_in: ValidatedFolder,
) -> str:
    final_file = StorageFile(name=chunk_meta.filename, storage=fs_upload)

    with open(final_file.path, "wb") as final_fp:
        for i in range(chunk_meta.total_chunks):
            chunk_name = f"{chunk_meta.upload_id}_{i}"
            chunk_file = StorageFile(name=chunk_name, storage=fs_chunk)

            if not chunk_file.exists:
                raise HTTPError(
                    400, _("Missing chunk %(chunk_id)s") % ({"chunk_id": i})
                )

            with chunk_file.open() as chunk_fp:
                while chunk := chunk_fp.read(chunk_file._storage.default_chunk_size):
                    final_fp.write(chunk)

            chunk_file.delete()

    file_create = FileCreate(
        name=chunk_meta.filename,
        location=folder_in.location,
        path=final_file.path,
        size=final_file.size,
        type=final_file.mime_type,
        owner=f"{current_user.first_name} {current_user.last_name}",
        folder_id=folder_in.id,
        user_id=current_user.id,
    )
    await storage_crud.create_file(session=session, file_create=file_create)

    return _("File uploaded successfully")
