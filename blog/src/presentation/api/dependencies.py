from typing import AsyncGenerator

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.services.posts import PostsService
from src.config import settings
from src.infrastructure.repo import MongoPostRepository, MongoCommentsRepository

async def get_mongo_connection() -> AsyncGenerator[AsyncIOMotorClient, None]:
    client = AsyncIOMotorClient(settings.MONGO_URL)
    yield client
    client.close()

async def get_posts_repository(
    mongo_client = Depends(get_mongo_connection)
) -> AsyncGenerator[MongoPostRepository, None]:
    yield MongoPostRepository(mongo_client=mongo_client)

async def get_comments_repository(
    mongo_client = Depends(get_mongo_connection)
) -> AsyncGenerator[MongoCommentsRepository, None]:
    yield MongoCommentsRepository(mongo_client=mongo_client)

async def get_posts_service(
    posts_repo = Depends(get_posts_repository),
    comments_repo = Depends(get_comments_repository)
) -> PostsService:
    return PostsService(posts_repo=posts_repo, comments_repo=comments_repo)
