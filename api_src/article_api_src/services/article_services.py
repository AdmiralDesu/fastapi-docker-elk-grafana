from fastapi import HTTPException, Response
import aiohttp
from database import get_async_session  # type: ignore
from models.article_models import ArticleType, Article
from schemas import (
    ArticleTypeCreationRequest,
    ArticleCreationResponse,
    ArticleCreationRequest,
)
from config import config


async def create_article_type_service(
    response: Response, article_type_info: ArticleTypeCreationRequest
) -> ArticleCreationResponse:
    try:
        new_article_type = ArticleType(
            name=article_type_info.name,
            description=article_type_info.description,
        )

        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            session.add(new_article_type)
            await session.commit()
        response.status_code = 201
        return ArticleCreationResponse(
            message="Новый тип статей успешно создан", article_id=new_article_type.id
        )
    except Exception as err:
        raise HTTPException(
            detail=f"При создании нового типа статей произошла ошибка {err}",
            status_code=500,
        )


async def create_article_service(
    response: Response, article_info: ArticleCreationRequest
) -> ArticleCreationResponse:

    try:
        form_data = aiohttp.FormData()
        form_data.add_field("name", "root")
        form_data.add_field("created_by", "admin")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.file_api_url}/file_api/files/create_folder", data=form_data
            ) as resp:
                if not resp.ok:
                    raise HTTPException(
                        detail=f"Не удалось создать папку для статьи. {await resp.text()}",
                        status_code=500,
                    )
                resp_data = await resp.json()
                folder_id = resp_data["folder_id"]
        new_article = Article(
            title=article_info.title,
            content=article_info.content,
            folder_id=folder_id,
            article_type=article_info.article_type,
            created_by=article_info.created_by,
        )

        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            session.add(new_article)
            await session.commit()
        response.status_code = 201
        return ArticleCreationResponse(
            message="Новый тип статей успешно создан", article_id=new_article.id
        )
    except Exception as err:
        raise HTTPException(
            detail=f"Произошла ошибка при создании новой статьи. {err=}",
            status_code=500,
        )
