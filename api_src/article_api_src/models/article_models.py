import datetime
from typing import Annotated

from sqlalchemy import Column, Text, UUID, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("now()"), index=True)
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("now()"),
        onupdate=datetime.datetime.now(),
    ),
]


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        unique=True,
    )
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False, index=True)
    folder_id: Mapped[str] = mapped_column(
        UUID, ForeignKey("app.files_tree.id"), nullable=False
    )
    icon_url: Mapped[str] = mapped_column(Text, nullable=True)
    article_type: Mapped[str] = mapped_column(
        ForeignKey("app.articles_types.id"), nullable=False
    )
    created_at: Mapped[created_at]
    created_by: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    updated_at: Mapped[updated_at]

    __table_args__ = ({"schema": "app"},)


class ArticleType(Base):
    __tablename__ = "articles_types"

    id: Mapped[str] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        unique=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, index=True)

    __table_args__ = ({"schema": "app"},)
