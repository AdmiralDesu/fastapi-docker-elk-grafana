from fastapi import APIRouter, Query, Response
from services import  push_archive, get_archive


archive_router = APIRouter(
    prefix="/archive"
)


@archive_router.get("/create_archive")
async def get_archive_of_folder(
        response: Response, # noqa
        folder_id: int = Query(...,description="ID папки из которой надо собрать архив"),
):
    """
    Метод для создания архива из папки
    :param folder_id: int
    :return: uuid по которому можно будет скачать архив
    """
    return await push_archive(
        folder_id=folder_id,
        response=response
    )


@archive_router.get("/get_archive")
async def get_archive_file(
        response: Response,
        archive_id: str = Query(..., description="ID, по которому можно получить архив")
):
    return await get_archive(archive_id, response=response)
