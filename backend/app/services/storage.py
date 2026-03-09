from pathlib import Path

from app.models import File, Folder
from app.schemas.storage import FilePublic, FolderPublic, FileFolderStatus
from app.deps.auth import SessionDep

from app.crud import storage as storage_crud


def to_public_file(file: File, folder_path: str | None = None) -> FilePublic:
    """
    Convet an internal File database model into a
    FilePublic schema.
    """
    return FilePublic(
        id=file.id,
        name=file.original_name,
        size=file.size,
        path=(
            file.path if folder_path is None else f"{folder_path}/{file.original_name}"
        ),
        type=file.mime_type,
        lastModified=file.updated_at,
        parent_id=file.folder_id,
    )


def to_public_folder(folder: Folder) -> FolderPublic:
    """
    Convet an internal Folder database model into a
    FolderPublic schema.
    """
    return FolderPublic(
        id=folder.id,
        name=folder.original_name,
        size=folder.size,
        path=folder.path,
        type=folder.mime_type,
        lastModified=folder.updated_at,
        parent_id=folder.parent_id,
    )


async def collect_files_for_folder(
    session: SessionDep, folder: Folder, base_path: str | None = None
):
    """
    Recursively collect all files inside a folder and its subfolders.

    Returns a list of tuples (disk_path, zip_path):
        - disk_path: absolute path of the file on the server
        - zip_path: relative path the file should have inside the zip archive
    """
    collected = []

    if base_path is None:
        base_path = Path(folder.original_name)

    files = await storage_crud.get_files_in_folder(session=session, folder_id=folder.id)
    for file in files:
        disk_path = Path(file.path)
        zip_path = base_path / file.original_name
        collected.append((disk_path, zip_path))

    subfolders = await storage_crud.get_folders_in_folder(
        session=session, folder_id=folder.id
    )
    for subfolder in subfolders:
        collected += await collect_files_for_folder(
            session=session,
            folder=subfolder,
            base_path=base_path / subfolder.original_name,
        )

    return collected


async def move_folders_to_trash_recursive(
    session: SessionDep, user_id: str, folder: Folder
):
    """
    Recursively moves a folder and all its contents to trash.

    Marks the folder an all nested subfolders and files as DELETED.
    Stores the original parent IDs and folder IDs to allow later restoration.
    """
    await storage_crud.update_folder(
        session=session,
        folder=folder,
        status=FileFolderStatus.DELETED,
        original_parent_id=folder.parent_id,
    )

    files = await storage_crud.get_files_in_folder(session=session, folder_id=folder.id)
    if files:
        for file in files:
            await storage_crud.update_file(
                session=session,
                file=file,
                status=FileFolderStatus.DELETED,
                original_folder_id=folder.id,
            )

    subfolders = await storage_crud.get_folders_in_folder(
        session=session, folder_id=folder.id
    )
    for subfolder in subfolders:
        await move_folders_to_trash_recursive(
            session=session, user_id=user_id, folder=subfolder
        )


async def get_first_uploaded_parent_id(
    session: SessionDep, folder: Folder
) -> str | None:
    """
    Recursively find the firs ancestor of a folder that is UPLOADED.
    """
    if not folder.parent_id:
        return None

    parent = await storage_crud.get_folder_by_id(
        session=session, folder_id=folder.parent_id
    )
    if parent and parent.status == FileFolderStatus.UPLOADED:
        return parent.id
    return await get_first_uploaded_parent_id(session=session, folder=parent)


async def restore_folders_recursive(session: SessionDep, folder: Folder):
    """
    Recursively restores a folder and all its contents.

    Sets folder status to UPLOADED and restores all files and subfolders
    that where previously deleted.
    """
    parent_id = await get_first_uploaded_parent_id(session=session, folder=folder)
    await storage_crud.update_folder(
        session=session,
        folder=folder,
        status=FileFolderStatus.UPLOADED,
        parent_id=parent_id,
    )
    files = await storage_crud.get_files_in_folder(
        session=session,
        folder_id=folder.id,
        status=FileFolderStatus.DELETED,
    )
    for file in files:
        await storage_crud.update_file(
            session=session,
            file=file,
            status=FileFolderStatus.UPLOADED,
            folder_id=folder.id,
            original_folder_id=None,
        )

    subfolders = await storage_crud.get_folders_in_folder(
        session=session,
        folder_id=folder.id,
        status=FileFolderStatus.DELETED,
    )
    for subfolder in subfolders:
        await restore_folders_recursive(session=session, folder=subfolder)
