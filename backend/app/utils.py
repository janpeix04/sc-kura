import uuid
import platform
import shutil
import zipfile

from typing import Callable, Awaitable, Any
from collections import deque

from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.crud import storage as storage_crud, crypto as crypto_crud
from app.models import File, Folder, EncryptedFolder
from app.schemas.crypto import EncryptedFolderTree, EncryptedFileTree
from app.schemas.storage import FolderStatus, FileStatus
from app.services.filesystem import FileSystemStorage, StorageFile

fs_upload = FileSystemStorage(settings.STORAGE_UPLOADS)


def score(item: File | Folder, now: datetime) -> int:
    hours_opened = (now - item.opened_at).total_seconds() / 3600
    hours_modified = (now - item.modified_at).total_seconds() / 3600
    hours_created = (now - item.created_at).total_seconds() / 3600

    return (
        (0.5 / (hours_opened + 1))
        + (0.3 / (hours_modified + 1))
        + (0.2 / (hours_created + 1))
    )


def get_total_disk_space() -> int:
    system = platform.system()

    if system == "Windows":
        path = "C:\\"
    else:
        path = "/"

    return shutil.disk_usage(path).total


async def add_folder_to_zip(
    *, session: AsyncSession, folder: Folder, zipf: zipfile.ZipFile, path: str
) -> None:
    current_path = f"{path}{folder.name}/"

    zipf.writestr(current_path, "")

    files = await storage_crud.get_files_in_folder(
        session=session, folder_id=folder.id, status=FileStatus.UPLOADED
    )

    for file in files:
        storage = StorageFile(name=file.stored_name, storage=fs_upload)

        if storage.exists():
            zipf.write(storage.path, arcname=current_path + file.name)

    subfolders = await storage_crud.get_folders_in_folder(
        session=session, parent_id=folder.id, status=FolderStatus.UPLOADED
    )

    for subfolder in subfolders:
        await add_folder_to_zip(
            session=session, folder=subfolder, zipf=zipf, path=current_path
        )


async def bfs_collect_all_files(
    root_id: uuid.UUID,
    get_children: Callable[[uuid.UUID], Awaitable[list[Any]]],
    get_files: Callable[[uuid.UUID], Awaitable[list[Any]]],
) -> list[Any]:
    queue = deque([root_id])
    all_files: list[Any] = []

    while queue:
        folder_id = queue.popleft()

        files = await get_files(folder_id)
        all_files.extend(files)

        children = await get_children(folder_id)
        for child in children:
            queue.append(child.id)

    return all_files


async def build_folder_tree(
    *, session: AsyncSession, folder: EncryptedFolder
) -> EncryptedFolderTree:
    children = await crypto_crud.get_folders_in_folder(
        session=session, parent_id=folder.id, status=FolderStatus.UPLOADED
    )

    files = await crypto_crud.get_files_in_folder(
        session=session, parent_id=folder.id, status=FileStatus.UPLOADED
    )

    child_trees = []

    for child in children:
        tree = await build_folder_tree(session=session, folder=child)

        child_trees.append(tree)

    return EncryptedFolderTree(
        id=folder.id,
        encrypted_key=folder.encrypted_key,
        encrypted_name=folder.encrypted_name,
        iv=folder.iv,
        folders=child_trees,
        files=[
            EncryptedFileTree(
                id=file.id,
                encrypted_key=file.encrypted_key,
                encrypted_name=file.encrypted_name,
                encrypted_name_iv=file.encrypted_name_iv,
                iv=file.iv,
            )
            for file in files
        ],
    )
