from fastapi import FastAPI
from config import config
from routers import file_router, archive_router
from contextlib import asynccontextmanager
import aioboto3
from botocore.exceptions import ClientError


@asynccontextmanager
async def lifespan(app: FastAPI):
    s3_session = aioboto3.Session()

    try:
        async with s3_session.client(
            "s3",
            endpoint_url=config.s3_info.endpoint,
            aws_access_key_id=config.s3_info.access_key,
            aws_secret_access_key=config.s3_info.secret_key
        ) as client:
            await client.head_bucket(Bucket=config.s3_info.bucket)
    except ClientError:
        async with s3_session.client(
                "s3",
                endpoint_url=config.s3_info.endpoint,
                aws_access_key_id=config.s3_info.access_key,
                aws_secret_access_key=config.s3_info.secret_key
        ) as client:
            await client.create_bucket(Bucket=config.s3_info.bucket)

    yield


app = FastAPI(
    title="File API",
    description="API for work with files",
    root_path=config.api_info.prefix,
    docs_url="/docs",
    lifespan=lifespan
)


app.include_router(file_router)
app.include_router(archive_router)

