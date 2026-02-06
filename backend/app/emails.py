from typing import Any
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from pydantic import EmailStr, BaseModel
from typing import List
from dataclasses import dataclass
from jinja2 import Template
from pathlib import Path

from app.core.config import settings


@dataclass
class EmailData:
    html_content: str
    subject: str


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
)


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (Path(__file__).parent / template_name).read_text()
    html_content = Template(template_str).render(context)
    return html_content


async def send_email(email_to: str, email_data: EmailData):
    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_to],
        body=email_data.html_content,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
