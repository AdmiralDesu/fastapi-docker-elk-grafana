"""
Модуль для описания работы селери
"""

from celery import Celery
from config import config
from celery_tasks import move_file_to_cache

celery = Celery(
    'file_api',
    broker=f"redis://{config.cache_info.redis_host}:{config.cache_info.redis_host}/0",
    backend=config.redis_url,
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


