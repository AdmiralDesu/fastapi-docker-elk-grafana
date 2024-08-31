from hashlib import sha256

import aioboto3
from fastapi import UploadFile, HTTPException, Response
from sqlalchemy import select, delete

from config import config
from database import get_async_session
from models.file_models import FileHash, File
from schemas import FileCreationRequest, BaseResponse, FileCreationResponse


async def calculate_hash(
        file: UploadFile
):
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


async def upload_file(file_info: FileCreationRequest, response: Response):
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


async def remove_file(file_key: str, response: Response):
    try:
        sessionmaker = await get_async_session()
        async with sessionmaker() as session, session.begin():
            await session.execute(delete(File).where(File.id == file_key))
            await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"При удалении файла возникла ошибка {e}")

    response.status_code = 200
    return BaseResponse(message=f"Файл с {file_key=} удален")
