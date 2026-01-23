from typing import Annotated
from fastapi import Depends

from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)


def get_session():
    with Session(bind=Session, autocommit=False, autoflush=False) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
