import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import Folder, File
from app.schemas.storage import FileCreate


def get_folder_by_id(*, session: Session, folder_id: uuid.UUID) -> Folder | None:
    stmt = select(Folder).where(Folder.id == folder_id)
    result = session.exec(stmt)
    return result.first()


def create_file(*, session: Session, file_create: FileCreate) -> File:
    file = File.model_validate(file_create)
    session.add(file)

    session.flush()

    update_folder_size_chain(
        session=session, folder_id=file.folder_id, size_delta=file.size
    )

    session.commit()
    session.refresh(file)
    return file


def update_folder_size_chain(
    *, session: Session, folder_id: uuid.UUID | None, size_delta: int
) -> None:
    while folder_id is not None:
        folder = get_folder_by_id(session=session, folder_id=folder_id)

        if folder is None:
            break

        folder.size += size_delta
        folder.modified_at = datetime.now(timezone.utc)

        session.add(folder)
        folder_id = folder.parent_id

    session.commit()
