import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from config import config

async_engine: AsyncEngine = create_async_engine(
    url=config.db_info.database_url,
    pool_size=config.db_info.pool_size,
    pool_pre_ping=True,
    echo=config.db_info.echo,
    future=True,
    max_overflow=config.db_info.max_overflow
)

async def get_async_session() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=async_engine,
        autocommit=False,
        expire_on_commit=False
    )


class Base(DeclarativeBase):
    ...
