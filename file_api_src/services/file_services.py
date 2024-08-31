from hashlib import sha256
from typing import Union

import aioboto3
from fastapi import UploadFile, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy import select, delete, update

from config import config
from database import get_async_session
from models.file_models import FileHash, File, ArchiveRequest, FileTree
from schemas import FileCreationRequest, BaseResponse, FileCreationResponse
from worker import create_archive


async def calculate_hash(
        file: UploadFile
):
    """
    Рассчитывает sha256 хэш файла
    :param file: Загруженный файл
    :return: sha256 хэш
    """
    sha256_hash = sha256()

    while content := await file.read(config.file_chunk):
        sha256_hash.update(content)

    return sha256_hash.hexdigest()


async def add_file_to_db(
        filename: str,
        file_size: int,
        file_hash: str,
        folder_id: int,
        created_by: str
):
    """
    Создает новую запись в app.files
    :param filename: Имя файла
    :param file_size: Размер файла
    :param file_hash: Хэш файла
    :param folder_id: ID папки
    :param created_by: Имя пользователя
    :return: Id новой записи в app.files
    """
    try:
        file_obj = File(
            name=filename,
            file_size=file_size,
            hash=file_hash,
            parent_id=folder_id,
            created_by=created_by
        )

        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            session.add(file_obj)
            await session.commit()
        return str(file_obj.id)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При записи файла в базу произошла ошибка {err}")



async def add_file_hash_to_db(
        file_hash: str,
        content_type: str
):
    """
    Создает новую запись в app.files_hashes
    :param file_hash: Хэш файла
    :param content_type: mime_type файла
    :return:
    """
    try:
        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            result = await session.execute(
                select(FileHash)
                .where(FileHash.id == file_hash)
            )

            if not result.scalar():
                file_hash_obj = FileHash(id=file_hash, mime_type=content_type)
                session.add(file_hash_obj)
                await session.commit()
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При записи хэша в базу произошла ошибка {err}")


async def upload_file_to_s3(
        file: UploadFile,
        file_key: str
):
    """
    Загружает файл на s3 хранилище
    :param file: Загруженный файл
    :param file_key: Ключ файла
    :return:
    """
    s3_session = aioboto3.Session()

    async with s3_session.client(
        "s3",
        endpoint_url=config.s3_info.endpoint,
        aws_access_key_id=config.s3_info.access_key,
        aws_secret_access_key=config.s3_info.secret_key
    ) as client:
        await client.upload_fileobj(
            file.file,
            config.s3_info.bucket,
            f"files/{file_key}"
        )


async def upload_file(
        file_info: FileCreationRequest,
        response: Response # noqa
):
    """
    Контроллер создания нового файла
    :param file_info: Информация о файле
    :return: ID нового файла или ошибка
    """
    file_hash = await calculate_hash(file=file_info.file)
    await file_info.file.seek(0)

    await upload_file_to_s3(
        file=file_info.file,
        file_key=file_hash
    )

    await add_file_hash_to_db(
        file_hash=file_hash,
        content_type=file_info.file.content_type
    )

    file_id = await add_file_to_db(
        filename=file_info.file.filename,
        file_size=file_info.file.size,
        file_hash=file_hash,
        folder_id=file_info.folder_id,
        created_by="admin"
    )

    response.status_code = 201
    return FileCreationResponse(message="Файл создан", file_key=file_id)


async def remove_file(
        file_key: str,
        response: Response # noqa
):
    """
    Контроллер удаления файла
    :param file_key: ID файла
    :return: Сообщение об удалении файла или ошибка
    """
    try:
        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            await session.execute(delete(File).where(File.id == file_key))
            await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"При удалении файла возникла ошибка {e}")

    response.status_code = 200
    return BaseResponse(message=f"Файл с {file_key=} удален")


async def push_archive(
        folder_id: int,
        response: Response
) -> BaseResponse:
    archive_request = ArchiveRequest(
        folder_id=folder_id,
        created_by="admin",
        status="pending"
    )

    sessionmaker = await get_async_session()
    async with sessionmaker() as session, session.begin():
        session.add(archive_request)
        await session.commit()

    create_archive.delay(folder_id, archive_request.id)

    response.status_code = 201

    return FileCreationResponse(message="Задача на создание архива создана", file_key=str(archive_request.id))


async def get_archive(
        archive_id: str,
        response: Response
) -> Union[BaseResponse, FileResponse]:
    sessionmaker = await get_async_session()
    async with sessionmaker() as session, session.begin():
        result = await session.execute(
            select(ArchiveRequest)
            .where(ArchiveRequest.id == archive_id)
            .where(ArchiveRequest.status == "finished")
        )

        request_obj: ArchiveRequest = result.scalars().one_or_none()

        if not request_obj:
            response.status_code = 404
            return BaseResponse(message="Архив еще не готов")

        result = await session.execute(
            select(FileTree.name)
            .filter(ArchiveRequest.folder_id == FileTree.id)
        )

        folder_name = result.scalar()

    return FileResponse(
        path=f"./temp/{archive_id}.zip",
        filename=f"{folder_name}.zip"
    )


async def rename_file_in_db(
        file_key: str,
        response: Response, # noqa
        new_name: str
) -> BaseResponse:
    """
    Изменяет имя файла на переданное
    :param file_key: Ключ файла
    :param new_name: Новое имя файла
    :return:
    """
    try:
        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            await session.execute(
                update(File)
                .where(File.id == file_key)
                .values(name=new_name)
            )
            await session.commit()

        response.status_code = 200

        return BaseResponse(message="Имя файла изменено")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При изменении имени файла произошла ошибка {err}")
