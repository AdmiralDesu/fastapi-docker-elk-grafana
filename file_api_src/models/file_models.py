import datetime
from typing import Annotated

from sqlalchemy import (
    Column,
    Integer,
    Text,
    UUID,
    TEXT,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("now()"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("now()"),
        onupdate=datetime.datetime.now(),
    )]


class File(Base):
    __tablename__ = 'files'

    id: Mapped[str] = Column(UUID, primary_key=True, index=True, server_default=text("gen_random_uuid()"), unique=True)
    name: Mapped[str] = Column(Text, nullable=False, index=True)
    file_size: Mapped[int] = Column(Integer, nullable=False)
    hash: Mapped[str] = Column(ForeignKey("app.files_hashes.id"), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    __table_args__ = (
        {"schema": "app"},
    )



class FileHash(Base):
    __tablename__ = 'files_hashes'

    id: Mapped[str] = Column(TEXT, primary_key=True, index=True, unique=True)
    mime_type: Mapped[str]
    created_at: Mapped[created_at]


    __table_args__ = (
        {"schema": "app"},
    )
