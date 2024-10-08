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

from base_model import Base

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("now()"), index=True)]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("now()"),
        onupdate=datetime.datetime.now(),
    )]
finished_at = Annotated[datetime.datetime, mapped_column(nullable=True)]

class FileTree(Base):
    __tablename__ = 'files_tree'

    id: Mapped[str] = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"), unique=True)
    name: Mapped[str] = Column(Text, index=True, nullable=False)
    parent_id: Mapped[str] = Column(UUID, ForeignKey('app.files_tree.id'), nullable=False, index=True)
    created_at: Mapped[created_at]
    created_by: Mapped[str] = Column(Text, nullable=False, index=True)
    updated_at: Mapped[updated_at]

    __table_args__ = (
        {"schema": "app"},
    )


class File(Base):
    __tablename__ = 'files'

    id: Mapped[str] = Column(UUID, primary_key=True, index=True, server_default=text("gen_random_uuid()"), unique=True)
    name: Mapped[str] = Column(Text, nullable=False, index=True)
    file_size: Mapped[int] = Column(Integer, nullable=False)
    hash: Mapped[str] = Column(ForeignKey("app.files_hashes.id"), nullable=False)
    parent_id: Mapped[str] = Column(UUID, ForeignKey('app.files_tree.id'), nullable=False, index=True)
    created_at: Mapped[created_at]
    created_by: Mapped[str] = Column(Text, nullable=False, index=True)
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


class ArchiveRequest(Base):
    __tablename__ = 'archive_requests'

    id: Mapped[str] = Column(UUID, primary_key=True, index=True, server_default=text("gen_random_uuid()"), unique=True)
    folder_id: Mapped[str] = Column(UUID, ForeignKey('app.files_tree.id'), nullable=False)
    status: Mapped[str]
    created_at: Mapped[created_at]
    created_by: Mapped[str] = Column(Text, nullable=False, index=True)
    finished_at: Mapped[finished_at]


    __table_args__ = (
        {"schema": "app"},
    )
