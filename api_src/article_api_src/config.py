import os

from pydantic import BaseModel


class DBInfo(BaseModel):
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    pool_size: int = os.environ.get("POOL_SIZE", 10)
    max_overflow: int = os.environ.get("MAX_OVERFLOW", 10)
    echo: bool = os.environ.get("ECHO", False)


class APIInfo(BaseModel):
    host: str = os.environ.get("HOST", "127.0.0.1")
    port: int = int(os.environ.get("PORT", 8003))
    prefix: str = os.environ.get("PREFIX", "/article_api")


class CacheInfo(BaseModel):
    redis_host: str = os.environ.get("REDIS_HOST", "127.0.0.1")
    redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
    ttl: int = int(os.environ.get("TTL", 1 * 60 * 60 * 6))  # 6 hours


class Config(BaseModel):
    db_info: DBInfo = DBInfo()
    api_info: APIInfo = APIInfo()
    cache_info: CacheInfo = CacheInfo()
    file_api_url: str = os.environ.get("FILE_API_URL", "http://127.0.0.1:8002")


config = Config()
