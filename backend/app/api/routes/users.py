from fastapi import APIRouter
from app.deps.auth import ValidatedUserRegisterForm
from app.schemas.users import UserCreate
from app.deps.auth import SessionDep
from app.crud import auth as auth_crud

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup/")
async def register_user(session: SessionDep, user_in: ValidatedUserRegisterForm) -> str:
    """
    Register a new User
    """
    user_create = UserCreate.model_validate(user_in)
    await auth_crud.create_user(session=session, user_create=user_create)
    return (
        "A verification email has been sent. "
        "Please verify your email to continue. "
        "Don't forget to check your spam or junk folder."
    )
