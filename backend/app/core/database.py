from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.crud import auth as auth_crud
from app.crud import storage as storage_crud
from app.schemas.users import UserCreate
from app.schemas.storage import FolderCreate

async_engine = create_async_engine(settings.DATABASE_URL, pool_size=10, max_overflow=10)


async def get_session() -> AsyncGenerator[AsyncGenerator, None]:
    async_session = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


async def init_db(session: AsyncSession):
    if settings.DEBUG:
        user = await auth_crud.get_user_by_email(
            session=session, email=settings.OWNER_EMAIL
        )
        if not user:
            user_create = UserCreate(
                first_name=settings.OWNER_FIRST_NAME,
                last_name=settings.OWNER_LAST_NAME,
                email=settings.OWNER_EMAIL,
                password=settings.OWNER_PASSWORD,
                is_verified=True,
            )
            user = await auth_crud.create_user(session=session, user_create=user_create)

        folder = await storage_crud.get_root_folder(session=session, user_id=user.id)

        if not folder:
            folder_create = FolderCreate(
                name="/",
                location="/",
                owner=f"{user.first_name} {user.last_name}",
                user_id=user.id,
            )
            folder = await storage_crud.create_folder(
                session=session, folder_create=folder_create
            )
