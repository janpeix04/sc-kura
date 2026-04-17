import io
import zipfile

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, UploadFile, Query
from fastapi.responses import FileResponse, StreamingResponse

from app import utils
from app.core.config import settings
from app.crud import storage as storage_crud
from app.deps.auth import SessionDep, CurrentUser
from app.deps.storage import ValidatedFile, ValidatedFolder, ValidatedNewFolder
from app.i18n import _
from app.schemas.storage import (
    AvailableSpace,
    FileCreate,
    FileUpdate,
    FolderPublic,
    FolderCreate,
    FolderUpdate,
    Breadcrumbs,
    FilePublic,
    FileStatus,
    FolderStatus,
    ItemsPublic,
)
from app.schemas.utils import HTTPError, add_responses
from app.services.filesystem import FileSystemStorage, StorageFile

router = APIRouter(prefix="/storage", tags=["storage"])

fs_upload = FileSystemStorage(settings.STORAGE_UPLOADS)
fs_chunk = FileSystemStorage(settings.STORAGE_CHUNK)


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


@router.get("/folder/trash/", response_model=FolderPublic, responses=add_responses(404))
async def get_trash_folder(
    session: SessionDep, current_user: CurrentUser
) -> FolderPublic:
    trash = await storage_crud.get_trash_folder(
        session=session, user_id=current_user.id
    )
    if not trash:
        raise HTTPError(404, _("Trash folder not found"))
    return trash


@router.post("/folder/trash/", response_model=str)
async def create_trash_folder(session: SessionDep, current_user: CurrentUser) -> str:
    folder_create = FolderCreate(
        name="trash/",
        path="/",
        owner=f"{current_user.first_name} {current_user.last_name}",
        user_id=current_user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Trash folder created successfully")


@router.get("/available/space/", response_model=AvailableSpace)
async def get_available_space(
    session: SessionDep, current_user: CurrentUser
) -> AvailableSpace:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)

    used = root.size
    total = utils.get_total_disk_space()
    available = total - used

    return AvailableSpace(total=total, used=used, available=available)


@router.get("/folders/{folder_id}/", response_model=list[FolderPublic])
async def get_folders_in_folder(
    session: SessionDep,
    folder_in: ValidatedFolder,
    status: FolderStatus = FolderStatus.UPLOADED,
) -> list[FolderPublic]:
    folders = await storage_crud.get_folders_in_folder(
        session=session, parent_id=folder_in.id, status=status
    )
    return folders


@router.post("/{folder_id}/", response_model=str)
async def create_folder(session: SessionDep, folder_create: ValidatedNewFolder) -> str:
    await storage_crud.create_folder(session=session, folder_create=folder_create)
    return _("Folder created successfully")


@router.patch(
    "/rename/folder/{folder_id}/", response_model=str, responses=add_responses(400)
)
async def rename_folder(
    session: SessionDep,
    folder_in: ValidatedFolder,
    payload: Annotated[FolderUpdate, Form()],
) -> str:
    if payload.name is None:
        raise HTTPError(status_code=400, msg=_("Please provide a valid folder name"))
    await storage_crud.rename_folder(
        session=session, folder=folder_in, new_name=payload.name
    )
    return _("Folder renamed successfully")


@router.delete("/folder/{folder_id}/", response_model=str)
async def delete_folder(session: SessionDep, folder_in: ValidatedFolder) -> str:
    files = await utils.bfs_collect_all_files(
        root_id=folder_in.id,
        get_children=lambda fid: storage_crud.get_folders_in_folder(
            session=session, parent_id=fid, status=FolderStatus.DELETED
        ),
        get_files=lambda fid: storage_crud.get_files_in_folder(
            session=session, folder_id=fid, status=FileStatus.DELETED
        ),
    )

    for file in files:
        storage = StorageFile(name=file.stored_name, storage=fs_upload)
        if storage.exists():
            storage.delete()

    await storage_crud.delete_folder(session=session, folder=folder_in)
    return _("Folder deleted successfully")


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


@router.get("/suggested/folders/", response_model=list[FolderPublic])
async def get_suggested_folders(
    session: SessionDep, current_user: CurrentUser
) -> list[FolderPublic]:
    folders = await storage_crud.get_suggested_folders(
        session=session, user_id=current_user.id
    )
    return folders


@router.get("/files/{folder_id}/", response_model=list[FilePublic])
async def get_files_in_folder(
    session: SessionDep,
    folder_in: ValidatedFolder,
    status: FileStatus = FileStatus.UPLOADED,
) -> list[FilePublic]:
    files = await storage_crud.get_files_in_folder(
        session=session, folder_id=folder_in.id, status=status
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
        type=file.content_type,
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


@router.patch(
    "/rename/file/{file_id}/", response_model=str, responses=add_responses(400)
)
async def rename_file(
    session: SessionDep, file_in: ValidatedFile, payload: Annotated[FileUpdate, Form()]
) -> str:
    if payload.name is None:
        raise HTTPError(status_code=400, msg=_("Please provide a valid file name"))

    new_name = payload.name
    if not Path(new_name).suffix:
        new_name = f"{new_name}{Path(file_in.name).suffix}"

    await storage_crud.rename_file(session=session, file=file_in, new_name=new_name)
    return _("File name renamed successfully")


@router.get("/suggested/files/", response_model=list[FolderPublic])
async def get_suggested_files(
    session: SessionDep, current_user: CurrentUser
) -> list[FilePublic]:
    files = await storage_crud.get_suggested_files(
        session=session, user_id=current_user.id
    )
    return files


@router.get(
    "/download/file/{file_id}/",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
        }
    },
)
async def download_file(file_in: ValidatedFile) -> FileResponse:
    storage = StorageFile(name=file_in.stored_name, storage=fs_upload)
    if not storage.exists():
        raise HTTPError(status_code=404, msg=_("File not found"))

    return FileResponse(
        path=storage.path, filename=file_in.name, media_type=file_in.type
    )


@router.get(
    "/download/folder/{folder_id}/",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/zip": {}},
        }
    },
)
async def download_folder(
    session: SessionDep, folder_in: ValidatedFolder
) -> StreamingResponse:
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        await utils.add_folder_to_zip(
            session=session, folder=folder_in, zipf=zipf, path=""
        )

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{folder_in.name}.zip"'},
    )


@router.patch("/move-to-trash/folder/{folder_id}/", response_model=str)
async def move_folder_to_trash(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    trash = await storage_crud.get_trash_folder(
        session=session, user_id=current_user.id
    )
    await storage_crud.move_folder_to_trash(
        session=session, folder=folder_in, parent_id=trash.id
    )
    return _("Folder moved to trash")


@router.patch("/move-to-trash/file/{file_id}/", response_model=str)
async def move_file_to_trash(
    session: SessionDep, current_user: CurrentUser, file_in: ValidatedFile
) -> str:
    trash = await storage_crud.get_trash_folder(
        session=session, user_id=current_user.id
    )
    await storage_crud.move_file_to_trash(
        session=session, file=file_in, parent_id=trash.id
    )
    return _("File moved to trash")


@router.delete("/empty/trash/", response_model=str)
async def empty_trash(session: SessionDep, current_user: CurrentUser) -> str:
    trash = await storage_crud.get_trash_folder(
        session=session, user_id=current_user.id
    )
    files = await storage_crud.get_all_files_by_status(
        session=session, user_id=current_user.id, status=FileStatus.DELETED
    )

    for file in files:
        storage = StorageFile(name=file.stored_name, storage=fs_upload)
        if storage.exists():
            storage.delete()
        if file.parent_id == trash.id:
            await storage_crud.delete_file(session=session, file=file)

    folders = await storage_crud.get_folders_in_folder(
        session=session, parent_id=trash.id
    )

    for folder in folders:
        await storage_crud.delete_folder(session=session, folder=folder)

    return _("Trash emptied successfully")


@router.patch("/restore/folder/{folder_id}/", response_model=str)
async def restore_folder(
    session: SessionDep, current_user: CurrentUser, folder_in: ValidatedFolder
) -> str:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    await storage_crud.restore_folder(
        session=session, folder=folder_in, parent_id=root.id
    )
    return _("Folder restored successfully")


@router.patch("/restore/file/{file_id}/", response_model=str)
async def restore_file(
    session: SessionDep, current_user: CurrentUser, file_in: ValidatedFile
) -> str:
    root = await storage_crud.get_root_folder(session=session, user_id=current_user.id)
    await storage_crud.restore_file(session=session, file=file_in, parent_id=root.id)
    return _("File restored successfully")


@router.get("/search/", response_model=ItemsPublic)
async def search_items(
    session: SessionDep, current_user: CurrentUser, q: Annotated[str, Query()]
) -> ItemsPublic:
    q = q.strip()

    if not q:
        return ItemsPublic(folders=[], files=[])

    folders = await storage_crud.get_likely_folders(
        session=session, user_id=current_user.id, query=q
    )

    files = await storage_crud.get_likely_files(
        session=session, user_id=current_user.id, query=q
    )

    return ItemsPublic(
        folders=folders,
        files=[FilePublic.model_validate(file) for file in files],
    )
