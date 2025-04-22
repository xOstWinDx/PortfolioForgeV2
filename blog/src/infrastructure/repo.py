from typing import Literal

from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.repo import IPostsRepository, PostsResultFromDB, ICommentsRepository, CommentsResultFromDB
from src.domain.comment import Comment
from src.domain.post import Post

class MongoMixin:

    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str, collection_name: str) -> None:
        self._client = mongo_client
        self.database = self._client.get_database(db_name)
        self.collection = self.database.get_collection(collection_name)


class MongoPostRepository(IPostsRepository, MongoMixin):

    async def get_post(self, post_id: str) -> Post | None:
        post = await self.collection.find_one({"_id"})
        return Post.from_dict(post) if post else None

    async def get_posts(
        self,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc"
    ) -> PostsResultFromDB:
        pass

    async def create_post(self, post: Post) -> Post:
        pass

    async def like_post(self, post_id: str, user_id: int) -> bool:
        pass

    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        pass


    async def delete_post(self, post_id: str) -> bool:
        pass


class MongoCommentsRepository(ICommentsRepository, MongoMixin):
    async def get_comments(self, post_id: str, last_id: str | None = None, limit: int = 10,
                           sort: Literal["asc", "desc"] = "desc") -> CommentsResultFromDB:
        pass

    async def create_comment(self, comment: Comment) -> Comment:
        pass

    async def like_comment(self, comment_id: str, user_id: int) -> bool:
        pass

    async def dislike_comment(self, comment_id: str, user_id: int) -> bool:
        pass

    async def create_answer(self, answer: Comment, comment_id: str) -> Comment:
        pass


    async def get_answers(self, comment_id: str, last_id: str | None = None, limit: int = 10,
                          sort: Literal["asc", "desc"] = "desc") -> CommentsResultFromDB:
        pass