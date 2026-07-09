from datetime import timedelta
from typing import Annotated
from pydantic import EmailStr

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from app import tasks
from app.deps.auth import SessionDep, ValidatedUserRegister
from app.crud import auth as auth_crud, storage as storage_crud
from app.core.config import settings
from app.core import security
from app.i18n import _
from app.schemas.users import UserUpdate
from app.schemas.storage import FolderCreate
from app.schemas.utils import add_responses, HTTPError, Token

router = APIRouter(tags=["auth"])


def _send_verify_email_address_email(
    *, user_in: ValidatedUserRegister, locale: str = "en"
):
    verify_token_expires = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    token = security.create_token(user_in.email, verify_token_expires)
    host = f"http://localhost:{settings.FRONTEND_PORT}"
    verification_link = host + router.url_path_for("verify_account", token=token)
    tasks.send_verify_email_address_email.delay(
        first_name=user_in.first_name,
        email_to=user_in.email,
        verification_link=verification_link,
        locale=locale,
    )


@router.post("/signup/", response_model=str)
async def sign_up(
    session: SessionDep, user_create: ValidatedUserRegister, locale: str = "en"
) -> str:
    user = await auth_crud.create_user(session=session, user_create=user_create)

    folder_create = FolderCreate(
        name="/",
        location="/",
        owner=f"{user.first_name} {user.last_name}",
        user_id=user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)

    folder_create = FolderCreate(
        name="trash/",
        location="/",
        owner=f"{user.first_name} {user.last_name}",
        user_id=user.id,
    )
    await storage_crud.create_folder(session=session, folder_create=folder_create)

    _send_verify_email_address_email(user_in=user_create, locale=locale)
    return _(
        "A verification email has been sent. "
        "Please verify your email to continue. "
        "Don't forget to check your spam or junk folder."
    )


@router.post("/login/", response_model=Token, responses=add_responses(400))
async def log_in(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await auth_crud.authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPError(status_code=400, msg=_("Invalid email address or password"))
    if not user.is_verified:
        raise HTTPError(
            status_code=400,
            msg=_(
                "Please verify your email address before logging in. "
                "Check your inbox for a confirmation link."
            ),
            loc="toast",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_token(user.email, access_token_expires)
    return Token(access_token=access_token)


@router.put(
    "/verify/account/{token}/", response_model=str, responses=add_responses(400)
)
async def verify_account(session: SessionDep, token: str) -> str:
    email = security.verify_token(token)
    user = await auth_crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPError(status_code=400, msg=_("Invalid or expired verification link"))
    if user.is_verified:
        return _("Email address already verified")
    user = await auth_crud.verify_user(session=session, user=user)
    return _("Your email address has been verified successfully")


@router.post("/forgot/password/", response_model=str, responses=add_responses(404))
async def forgot_password(
    session: SessionDep, email: Annotated[EmailStr, Form()], locale: str = "en"
) -> str:
    user = await auth_crud.get_user_by_email(session=session, email=email)

    if user:
        reset_token_expires = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
        token = security.create_token(email, reset_token_expires)
        host = f"http://localhost:{settings.FRONTEND_PORT}"
        reset_link = host + router.url_path_for("reset_password", token=token)

        tasks.send_reset_password_email.delay(
            first_name=user.first_name,
            email_to=email,
            reset_password_link=reset_link,
            locale=locale,
        )

    return _(
        "If an account exists for this email address, "
        "we've sent password reset instructions. "
        "Please check your inbox and spam or junk folder."
    )


@router.post("/reset/password/{token}/", responses=add_responses(400, 404))
async def reset_password(
    session: SessionDep, token: str, new_password: Annotated[str, Form()]
) -> str:
    email = security.verify_token(token=token)
    user = await auth_crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPError(status_code=404, msg=_("User not found"), loc="email")
    elif not user.is_verified:
        raise HTTPError(
            status_code=400,
            msg=_(
                "Please verify your email address before logging in. "
                "Check your inbox for a confirmation link."
            ),
            loc="unverified",
        )
    user_in = UserUpdate(password=new_password)
    user = await auth_crud.update_user(session=session, db_user=user, user_in=user_in)
    security.mark_token_as_used(token=token)
    return _("Password updated successfully")


@router.get("/expired/{token}/", response_model=bool)
async def is_token_expired(token: str) -> bool:
    security.verify_token(token=token)
    return security.is_token_already_used(token=token)
