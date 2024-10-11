from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    message: str = Field(..., description="Сообщение об ошибке или успехе")

class FileCreationResponse(BaseResponse):
    file_key: str = Field(..., description="ID файла")
