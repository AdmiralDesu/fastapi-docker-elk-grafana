import os
import redis
from config import config


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
