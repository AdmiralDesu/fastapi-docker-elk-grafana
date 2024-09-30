from fastapi import FastAPI
from routers import article_router

app = FastAPI()

app.include_router(article_router, prefix="/articles")
