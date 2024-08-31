import os

from pydantic import BaseModel


class DBInfo(BaseModel):
    database_url: str = os.environ.get('DATABASE_URL', "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    pool_size: int = os.environ.get('POOL_SIZE', 10)
    max_overflow: int = os.environ.get('MAX_OVERFLOW', 10)
    echo: bool = os.environ.get('ECHO', False)

class APIInfo(BaseModel):
    host: str = os.environ.get("HOST", "localhost")
    port: str = os.environ.get("PORT", 8001)
    prefix: str = os.environ.get("PREFIX", "/file_api")


class S3Info(BaseModel):
    endpoint: str = os.environ.get('ENDPOINT', "http://127.0.0.1:9000")
    bucket: str = os.environ.get('BUCKET', "files")
    access_key: str = os.environ.get('ACCESS_KEY', "minioadmin")
    secret_key: str = os.environ.get('SECRET_KEY', "minioadmin")

class CacheInfo(BaseModel):
    redis_host: str = os.environ.get("REDIS_HOST", "127.0.0.1")
    redis_port: int = os.environ.get("REDIS_PORT", 6379)
    ttl: int = os.environ.get("TTL", 1 * 60 * 60 * 6 ) # 6 hours


class Config(BaseModel):
    db_info: DBInfo = DBInfo()
    api_info: APIInfo = APIInfo()
    s3_info: S3Info = S3Info()
    cache_info: CacheInfo = CacheInfo()
    file_chunk: int = os.environ.get("CHUNK_SIZE", 1024 * 16)


config = Config()


