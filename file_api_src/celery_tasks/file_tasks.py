import os
import redis
from config import config
import boto3
import json


def move_file_to_cache(
        path_to_file: str,
        file_hash: str,
        file_id: str,
        file_name: str
):
    r = redis.Redis(host=config.cache_info.redis_host, port=config.cache_info.redis_port, db=1)

    if r.get(f"cache:{file_id}"):
        r.close()
        return
    path_to_cache = f"./cache/{file_hash}"
    os.rename(path_to_file, path_to_cache)

    file_info = {
        "path_to_cache": path_to_cache,
        "file_name": file_name
    }

    r.set(f"cache:{file_id}", json.dumps(file_info), nx=True, ex=config.cache_info.ttl)
    r.close()
    os.remove(path_to_file)


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
