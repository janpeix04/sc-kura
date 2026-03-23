from typing import Annotated
from fastapi import APIRouter, Form

from app.deps.auth import SessionDep
from app.schemas.users import UserRegister
from app.crud import auth as auth_crud

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/", response_model=str)
async def sign_up(session: SessionDep, user_create: Annotated[UserRegister, Form()]):
    await auth_crud.create_user(session=session, user_create=user_create)
    return "User registered successfully"
