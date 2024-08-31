"""
Роутер для работы с файлами
"""

from fastapi import APIRouter, Depends, Response

from schemas import (
    FileCreationRequest,
    FileCreationResponse,
    BaseResponse
)
from services import (
    upload_file,
    remove_file
)


file_router = APIRouter(
    prefix="/files"
)


@file_router.post("/create_file")
async def create_file(
        response: Response, # noqa
        file_info: FileCreationRequest = Depends(FileCreationRequest.as_form),
) -> FileCreationResponse:
    """
    Метод для записи нового файла.
    Рассчитывает хэш, заливает файл на s3, записывает данные в базу
    :param file_info: Модель с информацией о файле
    :return: id нового файла или ошибка
    """

    return await upload_file(file_info=file_info, response=response)


@file_router.delete("/delete_file")
async def delete_file(
        file_key: str,
        response: Response, # noqa
) -> BaseResponse:
    """
    Метод для удаления файла
    :param file_key: ID файла
    :return: Сообщение об удалении файла или ошибка
    """
    return await remove_file(file_key=file_key, response=response)
