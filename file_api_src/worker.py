"""
Модуль для описания работы селери
"""
import uuid
from zipfile import ZipFile

import psycopg
from celery import Celery, group, chord

from celery_tasks import move_file_to_cache, download_file
from config import config

celery = Celery(
    'file_api',
    broker=f"redis://{config.cache_info.redis_host}:{config.cache_info.redis_port}/0",
    backend=f"redis://{config.cache_info.redis_host}:{config.cache_info.redis_port}/0",
    CELERY_DEFAULT_QUEUE='file_api',
    timezone='Europe/Moscow',
    broker_connection_retry_on_startup=True
)


@celery.task(name='put_file_to_cache')
def put_file_to_cache(
        path_to_file: str,
        file_hash: str
):
    move_file_to_cache(
        path_to_file=path_to_file,
        file_hash=file_hash
    )


@celery.task(name="download_file_from_s3")
def download_file_from_s3(
        file_id: str,
        file_hash: str,
        file_name: str,
        archive_id: str
) -> tuple[str, str, str]:
    """
    Celery задача для скачивания файла из s3
    :param archive_id: ID архива
    :param file_name: Имя файла
    :param file_hash: ID файла из s3
    :param file_id: ID файла из базы
    :return:
    """
    return download_file(file_id=file_id, file_hash=file_hash), file_name, archive_id

@celery.task(name="archive_files")
def archive_files(*args):
    archive_id = args[0][0][2]

    path_to_archive = f"./temp/{archive_id}.zip"


    file_paths_and_names = [(x[0], x[1]) for x in args[0]]

    with ZipFile(path_to_archive, "w") as inzip:
        computed_names = []
        for file, name in file_paths_and_names:
            if name in computed_names:
                name = f"{uuid.uuid4()}.{name}"
            inzip.write(file, arcname=name)
            computed_names.append(name)

    return path_to_archive


@celery.task(name='create_archive')
def create_archive(
        folder_id: int,
        archive_id: str
):
    with psycopg.connect(config.db_info.database_url.replace("+asyncpg", "")) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                select id, hash, name from app.files where parent_id = {folder_id}
                """
            )
            all_files = cursor.fetchall()
            all_files = [[str(x[0]), x[1], x[2]] for x in all_files]

    chord(
        group(download_file_from_s3.s(file_id, file_hash, file_name, archive_id) for file_id, file_hash, file_name in all_files)
    )(archive_files.s())

    with psycopg.connect(config.db_info.database_url.replace("+asyncpg", "")) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                update app.archive_requests set status = 'finished' where id = '{archive_id}'
                """
            )
            conn.commit()
