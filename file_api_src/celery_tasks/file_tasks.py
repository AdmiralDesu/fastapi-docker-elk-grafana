import os
import redis
from config import config
import boto3

def move_file_to_cache(
        path_to_file: str,
        file_hash: str
):
    os.rename(path_to_file, f"./cache/{file_hash}")
    r = redis.Redis(host=config.cache_info.redis_host, port=config.cache_info.redis_port, db=1)
    r.set(f"{file_hash}", f"./{file_hash}", nx=True, ex=config.cache_info.ttl)
    r.close()
    os.remove(path_to_file)


def clear_cache():
    pass # TODO Сделать celery задачу для удаления файлов кэша каждые 6 часов


def download_file(
        file_id: str,
        file_hash: str
) -> str:
    """
    Задача для скачивания файла из s3
    :param file_id: Ключ файла в бд
    :param file_hash: Ключ файла в s3
    :return: Путь к скаченному файлу
    """
    path_to_file = f"./temp/{file_id}"
    s3_session  = boto3.Session()

    print(file_id)
    print(file_hash)

    s3_client = s3_session.client(
        "s3",
        endpoint_url=config.s3_info.endpoint,
        aws_access_key_id=config.s3_info.access_key,
        aws_secret_access_key=config.s3_info.secret_key
    )

    s3_client.download_file(
        config.s3_info.bucket,
        f"files/{file_hash}",
        path_to_file
    )

    s3_client.close()

    return path_to_file
