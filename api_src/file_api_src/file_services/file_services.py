import json
from hashlib import sha256
from tkinter.font import names
from typing import Union
from uuid import uuid4

import aioboto3
from fastapi import UploadFile, HTTPException, Response, BackgroundTasks
from fastapi.responses import FileResponse
from redis.asyncio import Redis
from sqlalchemy import select, delete, update
from pydantic import UUID4

from config import config
from database import get_async_session
from file_models.file_models import FileHash, File, ArchiveRequest, FileTree
from file_schemas import FileCreationRequest, BaseResponse, FileCreationResponse, FolderCreationRequest
from worker import create_archive, put_file_to_cache


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
        folder_id: str,
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
                .where(FileHash.id == file_hash) # noqa
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


async def get_file_from_s3(
        file_hash: str
) -> str:
    """
    Скачивает файл из s3 по хэшу
    :param file_hash: Хэш файла
    :return: Путь до файла
    """
    path_to_temp_file = f"./temp/{uuid4()}"
    s3_session = aioboto3.Session()
    async with s3_session.client(
            "s3",
            endpoint_url=config.s3_info.endpoint,
            aws_access_key_id=config.s3_info.access_key,
            aws_secret_access_key=config.s3_info.secret_key
    ) as client:
        await client.download_file(
            config.s3_info.bucket,
            f"files/{file_hash}",
            path_to_temp_file
        )
    return path_to_temp_file


async def upload_file(
        file_info: FileCreationRequest,
        response: Response # noqa
) -> FileCreationResponse:
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
) -> BaseResponse:
    """
    Контроллер удаления файла
    :param file_key: ID файла
    :return: Сообщение об удалении файла или ошибка
    """
    try:
        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            await session.execute(delete(File).where(File.id == file_key)) # noqa
            await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"При удалении файла возникла ошибка {e}")

    response.status_code = 200
    return BaseResponse(message=f"Файл с {file_key=} удален")


async def push_archive(
        folder_id: str,
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

    return FileCreationResponse(
        message="Задача на создание архива создана",
        file_key=str(archive_request.id)
    )


async def get_archive(
        archive_id: str,
        response: Response # noqa
) -> Union[BaseResponse, FileResponse]:
    """
    Отдает статус создания архива или файл архива
    :param archive_id: ID архива
    :return: Статус архива или файл архива
    """
    sessionmaker = await get_async_session()
    async with sessionmaker() as session, session.begin():
        result = await session.execute(
            select(ArchiveRequest)
            .where(
                ArchiveRequest.id == archive_id, # noqa
                ArchiveRequest.status == "finished" # noqa
            )
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
                .where(File.id == file_key) # noqa
                .values(name=new_name)
            )
            await session.commit()

        response.status_code = 200

        return BaseResponse(message="Имя файла изменено")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При изменении имени файла произошла ошибка {err}")


async def download_file_from_s3(
        file_id: str,
        response: Response, # noqa
        background_tasks: BackgroundTasks # noqa
) -> Union[FileResponse, BaseResponse]:
    """
    Отдает файл из хранилища либо их кэша
    :param file_id: ID файла
    :return: Файл или сообщение об ошибке
    """
    try:
        r = Redis(host=config.cache_info.redis_host, port=config.cache_info.redis_port, db=1)

        file_info = await r.get(f"cache:{file_id}")

        await r.close()

        if file_info:
            file_info = json.loads(file_info)
            return FileResponse(
                path=file_info['path_to_cache'],
                filename=file_info['file_name']
            )

        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            result = await session.execute(
                select(File)
                .where(File.id == file_id) # noqa
            )
            await session.commit()

            file_obj: File = result.scalars().one_or_none()

        if not file_obj:
            response.status_code = 404
            return BaseResponse(message="Файл не найден")
        try:
            path_to_file = await get_file_from_s3(file_obj.hash)
        except Exception as err:
            response.status_code = 404
            return BaseResponse(message=f"Файл найден в базе, но не найден в хранилище {err}")

        response.status_code = 200
        background_tasks.add_task(put_file_to_cache.delay, path_to_file, file_obj.hash, file_id, file_obj.name)
        return FileResponse(
            path=path_to_file,
            filename=file_obj.name
        )

    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При скачивании файла произошла ошибка {err}")


async def create_new_folder(
        response: Response,
        folder_info: FolderCreationRequest
):
    try:
        new_uuid = uuid4()
        new_folder_obj = FileTree(
            id=new_uuid,
            name=folder_info.name,
            parent_id=new_uuid if not folder_info.parent_id else folder_info.parent_id,
            created_by=folder_info.created_by
        )

        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            session.add(new_folder_obj)
            await session.commit()

        return FileCreationResponse(message="Папка успешно создана", file_key=str(new_folder_obj.id))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"При создании папки произошла ошибка {err}")
