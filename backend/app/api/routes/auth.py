from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.deps.auth import SessionDep, ValidatedUserRegister
from app.crud import auth as auth_crud
from app.schemas.utils import add_responses, HTTPError, Token
from app.core.config import settings
from app.core import security
from app.services.email import generate_verify_email_address_email, send_email
from app.i18n import _

router = APIRouter(tags=["auth"])


async def _send_verify_email_address_email(
    *, user_in: ValidatedUserRegister, locale: str = "en"
):
    verify_token_expires = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    token = security.create_token(user_in.email, verify_token_expires)
    host = f"http://localhost:{settings.FRONTEND_PORT}"
    verification_link = host + router.url_path_for("verify_account", token=token)
    email_data = generate_verify_email_address_email(
        first_name=user_in.first_name,
        verification_link=verification_link,
        locale=locale,
    )
    await send_email(user_in.email, email_data)


async def _send_verify_email_address_email(
    *, user_in: ValidatedUserRegister, locale: str = "en"
):
    verify_token_expires = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    token = security.create_token(user_in.email, verify_token_expires)
    host = f"http://localhost:{settings.FRONTEND_PORT}"
    verification_link = host + router.url_path_for("verify_account", token=token)
    email_data = generate_verify_email_address_email(
        first_name=user_in.first_name,
        verification_link=verification_link,
        locale=locale,
    )
    await send_email(user_in.email, email_data)


@router.post("/signup/", response_model=str)
async def sign_up(
    session: SessionDep, user_create: ValidatedUserRegister, locale: str = "en"
) -> str:
    await auth_crud.create_user(session=session, user_create=user_create)
    await _send_verify_email_address_email(user_in=user_create, locale=locale)
    return _("User registered successfully")


@router.post("/login/", response_model=Token, responses=add_responses(400))
async def log_in(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await auth_crud.authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPError(status_code=400, msg=_("Incorrect email or passowrd"))
    if not user.is_verified:
        raise HTTPError(
            status_code=400,
            msg=_(
                "Please verify your email address before logging in. "
                "Check your inbox for a confirmation link."
            ),
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
        raise HTTPError(status_code=400, msg=_("Incorrect email or password"))
    if user.is_verified:
        return _("Email address already verified")
    return _("Your email address has been verified successfully")
