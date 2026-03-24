from fastapi import APIRouter

from app.deps.auth import SessionDep, ValidatedUserRegister
from app.crud import auth as auth_crud

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/", response_model=str)
async def sign_up(session: SessionDep, user_create: ValidatedUserRegister):
    await auth_crud.create_user(session=session, user_create=user_create)
    return "User registered successfully"
