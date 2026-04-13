import asyncio
import time


from app.i18n import _
from app.celery import app
from app.services.email import (
    send_email,
    generate_verify_email_address_email,
    generate_reset_password_email,
)


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
                "progress": i,  # 👈 current progress
                "total": total,  # 👈 total steps
                "current_file": file,
            },
        )

    return {
        "progress": total,
        "total": total,
        "message": "completed",
    }
