from typing import Annotated
from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter
from app.schemas.uitls import add_responses, Tokens, HTTPError
from app.deps.auth import SessionDep
from app.crud import auth as auth_crud
from app.core.config import settings
from app.core import security

router = APIRouter(tags=["login"])


@router.post("/login/", response_model=Tokens, responses=add_responses(400))
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPError(status_code=400, msg="Incorrect email or password")
    elif not user.is_verified:
        raise HTTPError(
            status_code=400,
            msg=(
                "Please verify your email address before logging in. "
                "Check your inbox for a confirmation link."
            ),
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return Tokens(
        access_token=security.create_token(
            str(user.id), expires_delta=access_token_expires
        ),
        refresh_token=security.create_token(
            str(user.id), expires_delta=refresh_token_expires
        ),
    )


@router.post(
    "/login/refresh-token/", response_model=Tokens, responses=add_responses(401)
)
async def refresh_access_token(session: SessionDep, refresh_token: str):
    """
    User refresh token to get a new access token
    """
    try:
        payload = security.decode_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPError(status_code=401, msg="Invalid refresh token")
    except Exception:
        raise HTTPError(status_code=401, msg="Invalid or expired refresh token")

    user = await auth_crud.get_user_by_id(session=session, id=user_id)
    if not user:  # or not user.is_verified
        raise HTTPError(status_code=401, msg="User no longer active")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return Tokens(
        access_token=security.create_token(
            str(user.id), expires_delta=access_token_expires
        ),
        refresh_token=security.create_token(
            str(user.id), expires_delta=refresh_token_expires
        ),
    )


@router.put("/verify/account/{token}/", responses=add_responses(400))
async def verify_account(
    *,
    session: SessionDep,
    token: str,
) -> str:
    email = security.verify_token(token=token)
    user = await auth_crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPError(status_code=400, msg="Incorrect email or password")
    if user.is_verified:
        return "Email address already verified"

    user = await auth_crud.verify_user(session=session, db_user=user)
    return "Your email has been verified successfully!"
