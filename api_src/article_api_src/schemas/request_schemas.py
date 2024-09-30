from pydantic import BaseModel, UUID4
from fastapi import Form


class ArticleCreationRequest(BaseModel):
    title: str
    content: str
    article_type: str
    created_by: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(..., description="Заголовок статьи"),
        content: str = Form(..., description="Содержание статьи"),
        article_type: str = Form(..., description="Вид статьи"),
        created_by: str = Form("admin", description="Кем была создана статья"),
    ):
        return cls(
            title=title,
            content=content,
            created_by=created_by,
            article_type=article_type,
        )


class ArticleTypeCreationRequest(BaseModel):
    name: str
    description: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., description="Название типа статьи"),
        description: str = Form(..., description="Описания типа статьи"),
    ):
        return cls(
            name=name,
            description=description,
        )
