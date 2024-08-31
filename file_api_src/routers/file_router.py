"""
Роутер для работы с файлами
"""

from fastapi import APIRouter, Depends, Response

from schemas import (
    FileCreationRequest
)
from services import upload_file, remove_file

file_router = APIRouter(
    prefix="/files"
)


@file_router.post("/create_file")
async def create_file(
        response: Response,
        file_info: FileCreationRequest = Depends(FileCreationRequest.as_form),
):

    return await upload_file(file_info=file_info, response=response)


@file_router.delete("/delete_file")
async def delete_file(
        file_key: str,
        response: Response,
):
    return await remove_file(file_key=file_key, response=response)
