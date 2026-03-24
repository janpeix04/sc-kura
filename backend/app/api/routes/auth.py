from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.deps.auth import SessionDep, ValidatedUserRegister
from app.crud import auth as auth_crud
from app.schemas.utils import add_responses, HTTPError, Token
from app.core.config import settings
from app.core.security import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/", response_model=str)
async def sign_up(session: SessionDep, user_create: ValidatedUserRegister) -> str:
    await auth_crud.create_user(session=session, user_create=user_create)
    return "User registered successfully"


@router.post("/login/", response_model=Token, responses=add_responses(400))
async def log_in(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await auth_crud.authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPError(status_code=400, msg="Incorrect email or passowrd")
    if not user.is_verified:
        raise HTTPError(
            status_code=400,
            msg=(
                "Please verify your email address before logging in. "
                "Check your inbox for a confirmation link."
            ),
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(user.email, access_token_expires)
    return Token(access_token=access_token)
