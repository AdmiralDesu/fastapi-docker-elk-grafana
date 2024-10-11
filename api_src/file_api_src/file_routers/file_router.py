"""
Роутер для работы с файлами
"""

from fastapi import APIRouter, Depends, Response, Query, BackgroundTasks
from pydantic import UUID4
from starlette.responses import FileResponse

from schemas import (
    FileCreationRequest,
    FileCreationResponse,
    BaseResponse,
    FolderCreationRequest,
)
from services import (
    upload_file,
    remove_file,
    rename_file_in_db,
    download_file_from_s3,
    create_new_folder,
)

file_router = APIRouter(prefix="/files")


@file_router.post("/create_file")
async def create_file(
    response: Response,  # noqa
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
    response: Response,  # noqa
) -> BaseResponse:
    """
    Метод для удаления файла
    :param file_key: ID файла
    :return: Сообщение об удалении файла или ошибка
    """
    return await remove_file(file_key=file_key, response=response)


@file_router.put("/rename_file")
async def rename_file(
    response: Response,  # noqa
    file_key: str = Query(..., description="ID файла"),
    new_name: str = Query(..., description="Новое имя для файла"),
):
    """
    Метод для изменения имени файла
    :param file_key: ID файла
    :param new_name: Новое имя файла
    :return: Сообщение об изменении имени файла или ошибка
    """
    return await rename_file_in_db(
        file_key=file_key, response=response, new_name=new_name
    )


@file_router.get("/download_file")
async def download_file(
    response: Response,  # noqa
    background_tasks: BackgroundTasks,  # noqa
    file_id: str = Query(..., description="ID файла"),
) -> FileResponse:
    """
    Метод для скачивания файла
    :param file_id: ID файла
    :return: Файл или ошибка
    """
    return await download_file_from_s3(
        file_id=file_id, response=response, background_tasks=background_tasks
    )


@file_router.post("/create_folder")
async def create_folder(
    response: Response,  # noqa
    folder_info: FolderCreationRequest = Depends(FolderCreationRequest.as_form),
) -> FileCreationResponse:
    """
    Метод для создания папки
    :param folder_info: Информация о создаваемой папке
    :return: uuid Новой папки
    """
    return await create_new_folder(response=response, folder_info=folder_info)
