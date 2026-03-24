from typing import Annotated

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError

from fastapi import Depends, Form
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.schemas.utils import error_codes, HTTPError, TokenData
from app.schemas.users import UserBase, UserRegister
from app.crud import auth as auth_crud
from app.core.security import oauth2_scheme
from app.models import User
from app.core.config import settings

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


@error_codes(401, 403, 404)
async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        token_data = TokenData(**payload)
    except ExpiredSignatureError:
        raise HTTPError(status_code=401, msg="Expired credentials")
    except (InvalidTokenError, ValidationError):
        raise HTTPError(status_code=403, msg="Could not validate credentials")
    user = await auth_crud.get_user_by_email(session=session, email=token_data.sub)
    if not user:
        raise HTTPError(status_code=404, msg="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@error_codes(409)
async def validate_user(session: SessionDep, user_in: UserBase) -> UserBase:
    user = await auth_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPError(
            status_code=409, msg="User with this email already exists", loc="email"
        )
    return user_in


async def validate_user_register_form(
    session: SessionDep, user_in: Annotated[UserRegister, Form()]
) -> UserRegister:
    return await validate_user(session=session, user_in=user_in)


ValidatedUserRegister = Annotated[UserRegister, Depends(validate_user_register_form)]
