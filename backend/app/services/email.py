from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class EmailData:
    subject: str
    html_content: str


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
)


async def send_email(email_to: str, email_data: EmailData):
    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_to],
        body=email_data.html_content,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
