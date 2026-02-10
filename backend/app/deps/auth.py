from typing import Annotated

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session

from app.schemas.users import UserBase, UserRegisterForm
from app.schemas.uitls import error_codes, HTTPError, TokenPayload
from app.crud import auth as auth_crud
from app.core.config import settings
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


@error_codes(409)
async def validate_user(session: SessionDep, user_in: UserBase) -> UserBase:
    existing_user = await auth_crud.get_user_by_email(
        session=session, email=user_in.email
    )
    if existing_user:
        raise HTTPError(
            status_code=409,
            msg="User with this email already exists",
            loc="email",
        )
    return user_in


@error_codes(409)
async def validate_user_register_form(
    session: SessionDep,
    user_in: Annotated[UserRegisterForm, Depends(UserRegisterForm.as_form)],
) -> UserRegisterForm:
    return await validate_user(session, user_in)


ValidatedUserRegisterForm = Annotated[
    UserRegisterForm, Depends(validate_user_register_form)
]


@error_codes(401, 403, 404)
async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except ExpiredSignatureError:
        raise HTTPError(status_code=401, msg="Expired credentials")
    except (InvalidTokenError, ValidationError):
        raise HTTPError(status_code=403, msg="Could not validate credentials")
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPError(status_code=404, msg="User not found")
    return user


async def get_current_active_superuser(current_user: "CurrentUser") -> User:
    if not current_user.is_superuser:
        raise HTTPError(status_code=403, msg="The user don't have enough privileges")
    return current_user


async def get_current_active_user(current_user: "CurrentUser") -> User:
    if current_user.is_superuser:
        raise HTTPError(status_code=403, msg="User must not be admin")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
SuperUser = Annotated[User, Depends(get_current_active_superuser)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
