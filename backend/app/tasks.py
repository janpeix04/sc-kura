import uuid
import asyncio
import time


from app.celery import app
from app.core.config import settings
from app.core.database_sync import get_session
from app.crud import storage_sync as storage_sync_crud
from app.i18n import _
from app.services.email import (
    send_email,
    generate_verify_email_address_email,
    generate_reset_password_email,
)
from app.services.filesystem import StorageFile, FileSystemStorage
from app.schemas.storage import FileCreate

fs_upload = FileSystemStorage(settings.STORAGE_UPLOADS)
fs_temp = FileSystemStorage(settings.STORAGE_TEMP)


@app.task
def send_verify_email_address_email(
    first_name: str, email_to: str, verification_link: str, locale: str = "en"
) -> str:
    email_data = generate_verify_email_address_email(
        first_name=first_name,
        verification_link=verification_link,
        locale=locale,
    )
    asyncio.run(send_email(email_to, email_data))
    return _("Email sent to %(email_to)s") % {"email_to": email_to}


@app.task
def send_reset_password_email(
    first_name: str, email_to: str, reset_password_link: str, locale: str = "en"
) -> str:
    email_data = generate_reset_password_email(
        first_name=first_name, reset_password_link=reset_password_link, locale=locale
    )
    asyncio.run(send_email(email_to, email_data))
    return _("Email sent to %(email_to)s") % {"email_to": email_to}


@app.task(bind=True)
def upload_files_task(self, files: list[str]):
    total = len(files)

    for i, file in enumerate(files, start=1):
        # simulate upload
        time.sleep(1)

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": i,
                "total": total,
                "current_file": file,
            },
        )

    return {
        "progress": total,
        "total": total,
        "message": "completed",
    }


@app.task(bind=True)
def process_uploaded_files(
    self,
    *,
    filenames: list[str],
    owner: str,
    location: str,
    user_id: uuid.UUID,
    folder_id: uuid.UUID,
):
    errors: list[str] = []
    total = len(filenames)

    def progress_callback(done: int, success: int = 0, error: str | None = None):
        if error:
            errors.append(error)

        self.update_state(
            state="STARTED",
            meta={
                "progress": int(done / total * 100) if total else 100,
                "done": done,
                "total": total,
                "errors": errors,
            },
        )

    with get_session() as session:
        for i, name in enumerate(filenames, start=1):
            try:
                temp_storage = StorageFile(name=name, storage=fs_temp)

                storage = StorageFile(name=name, storage=fs_upload)
                storage.write(temp_storage.open())

                temp_storage.delete()

                file_create = FileCreate(
                    name=storage.name,
                    location=location,
                    path=storage.path,
                    size=storage.size,
                    type=storage.mime_type,
                    owner=owner,
                    folder_id=folder_id,
                    user_id=user_id,
                )

                storage_sync_crud.create_file(session=session, file_create=file_create)

                progress_callback(i, 1)

            except Exception as e:
                progress_callback(i, 0, str(e))

    return {
        "success_count": total - len(errors),
        "total_count": total,
        "errors": errors,
        "message": f"Processed {total - len(errors)} of {total} files",
    }
