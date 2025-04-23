from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient

from auth.src.application.interfaces.repo import IUserRepository
from src.application.interfaces.repo import IPostsRepository, ICommentsRepository
from src.application.services.comments import CommentsService
from src.application.services.posts import PostsService
from src.config import settings
from src.infrastructure.repo import MongoPostRepository, MongoCommentsRepository

AUTH_HEADER_NOTE = (
    "<ul>"
    "<li>Передайте заголовок <code>Authorization: Bearer &lt;token&gt;</code></li>"
    "</ul>"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login", auto_error=False, description=AUTH_HEADER_NOTE
)


async def get_mongo_connection() -> AsyncGenerator[AsyncIOMotorClient, None]:
    client = AsyncIOMotorClient(settings.MONGO_URL)
    yield client
    client.close()


async def get_user_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_connection),
) -> AsyncGenerator[MongoPostRepository, None]:
    yield MongoPostRepository(
        mongo_client=mongo_client,
        db_name=settings.MONGO_DB,
        collection_name=settings.USERS_COLLECTION,
    )


async def get_posts_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_connection),
) -> AsyncGenerator[MongoPostRepository, None]:
    yield MongoPostRepository(
        mongo_client=mongo_client,
        db_name=settings.MONGO_DB,
        collection_name=settings.POSTS_COLLECTION,
    )


async def get_comments_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_connection),
) -> AsyncGenerator[MongoCommentsRepository, None]:
    yield MongoCommentsRepository(
        mongo_client=mongo_client,
        db_name=settings.MONGO_DB,
        collection_name=settings.COMMENTS_COLLECTION,
    )


async def get_posts_service(
    posts_repo: IPostsRepository = Depends(get_posts_repository),
    comments_repo: ICommentsRepository = Depends(get_comments_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> PostsService:
    return PostsService(
        posts_repo=posts_repo, comments_repo=comments_repo, user_repo=user_repo
    )


async def get_comments_service(
    posts_repo: IPostsRepository = Depends(get_posts_repository),
    comments_repo: ICommentsRepository = Depends(get_comments_repository),
    users_repo: IUserRepository = Depends(get_user_repository),
) -> CommentsService:
    return CommentsService(
        comments_repo=comments_repo, posts_repo=posts_repo, users_repo=users_repo
    )
