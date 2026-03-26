import asyncio

from app.i18n import _
from app.celery import app
from app.services.email import (
    send_email,
    generate_verify_email_address_email,
)


@app.task
def send_verify_email_address_email(
    first_name: str, email_to: str, verification_link: str, locale: str = "en"
):
    email_data = generate_verify_email_address_email(
        first_name=first_name,
        verification_link=verification_link,
        locale=locale,
    )
    asyncio.run(send_email(email_to, email_data))
    return _("Email sent to %(email_to)s") % {"email_to": email_to}
