from pydantic import BaseModel


class BaseResponse(BaseModel):
    message: str


class ArticleCreationResponse(BaseResponse):
    article_id: str
