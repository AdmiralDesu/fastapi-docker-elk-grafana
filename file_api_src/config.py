import os

from pydantic import BaseModel


class DBInfo(BaseModel):
    database_url: str = os.environ['DATABASE_URL']
    pool_size: int = os.environ.get('POOL_SIZE', 10)
    max_overflow: int = os.environ.get('MAX_OVERFLOW', 10)
    echo: bool = os.environ.get('ECHO', False)

class APIInfo(BaseModel):
    host: str = os.environ['HOST']
    port: str = os.environ['PORT']
    prefix: str = os.environ['PREFIX']


class S3Info(BaseModel):
    endpoint: str = os.environ['ENDPOINT']
    bucket: str = os.environ['BUCKET']
    access_key: str = os.environ['ACCESS_KEY']
    secret_key: str = os.environ['SECRET_KEY']


class Config(BaseModel):
    db_info: DBInfo = DBInfo()
    api_info: APIInfo = APIInfo()
    s3_info: S3Info = S3Info()


config = Config()


