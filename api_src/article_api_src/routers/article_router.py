from fastapi import APIRouter, Response, Depends

from models.article_models import Article, ArticleType  # type: ignore
from schemas import (
    ArticleTypeCreationRequest,
    ArticleCreationRequest,
    ArticleCreationResponse,
)
from services import create_article_type_service, create_article_service

article_router = APIRouter(prefix="/articles")


@article_router.post("/create_article")
async def create_article(
    response: Response,  # noqa
    article_info: ArticleCreationRequest = Depends(ArticleCreationRequest.as_form),
) -> ArticleCreationResponse:
    """
    Метод для создания новой статьи
    :param article_info: Информация для создания новой статьи
    :return: ID новой статьи или ошибка
    """
    return await create_article_service(article_info=article_info, response=response)


@article_router.post("/create_article_type")
async def create_article_type(
    response: Response,  # noqa
    article_type_info: ArticleTypeCreationRequest = Depends(
        ArticleTypeCreationRequest.as_form
    ),
) -> ArticleCreationResponse:
    """
    Метод для создания нового типа статей
    :param article_type_info: Информация для создания типа статьи
    :return: ID нового типа или ошибка
    """
    return await create_article_type_service(
        article_type_info=article_type_info, response=response
    )
