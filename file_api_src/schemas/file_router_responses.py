from pydantic import BaseModel


class BaseResponse(BaseModel):
    message: str

class FileCreationResponse(BaseResponse):
    file_key: str
