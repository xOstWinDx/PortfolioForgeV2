from typing import Literal

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.repo import (
    IPostsRepository,
    PostsResultFromDB,
    ICommentsRepository,
    CommentsResultFromDB,
)
from src.domain.comment import Comment
from src.domain.exceptions import PostNotFoundException
from src.domain.post import Post


class MongoMixin:

    def __init__(
        self, mongo_client: AsyncIOMotorClient, db_name: str, collection_name: str
    ) -> None:
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
        sort: Literal["asc", "desc"] = "desc",
    ) -> PostsResultFromDB:
        pipline = [
            {
                "$match": {
                    **(
                        {
                            "_id": (
                                {"$lt": ObjectId(last_id)}
                                if sort == "desc"
                                else {"$gt": ObjectId(last_id)}
                            )
                        }
                        if last_id
                        else {}
                    )
                }
            },
            {"$sort": {"_id": -1 if sort == "desc" else 1}},
            {"$limit": limit + 1},
        ]
        cursor = self.collection.aggregate(pipline)
        result = [Post.from_dict(post) async for post in cursor]
        has_next = len(result) > limit
        return PostsResultFromDB(posts=result[:limit], has_next=has_next)

    async def create_post(self, post: Post) -> Post:
        res = await self.collection.insert_one(
            {
                "_id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author.to_dict(),
                "dislikes": post.dislikes,
                "likes": post.likes,
                "created_at": post.created_at,
                "comments_count": post.comments_count,
                "images": post.images,
            }
        )
        assert res.inserted_id, "Something went wrong"
        return post

    async def like_post(self, post_id: str, user_id: int) -> bool:
        if not await self.collection.find_one({"_id": ObjectId(post_id)}):
            raise PostNotFoundException(
                f"Can't like post, post not found with id: {post_id}"
            )

        res = await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"likes": user_id},
                "$pull": {"dislikes": user_id},
            },
        )
        return bool(res.modified_count)

    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        if not await self.collection.find_one({"_id": ObjectId(post_id)}):
            raise PostNotFoundException(
                f"Can't dislike post, post not found with id: {post_id}"
            )

        res = await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"dislikes": user_id},
                "$pull": {"likes": user_id},
            },
        )
        return bool(res.modified_count)

    async def delete_post(self, post_id: str) -> bool:
        pass


class MongoCommentsRepository(ICommentsRepository, MongoMixin):
    async def get_comments(
        self,
        post_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> CommentsResultFromDB:
        pass

    async def create_comment(self, comment: Comment) -> Comment:
        pass

    async def like_comment(self, comment_id: str, user_id: int) -> bool:
        pass

    async def dislike_comment(self, comment_id: str, user_id: int) -> bool:
        pass

    async def create_answer(self, answer: Comment, comment_id: str) -> Comment:
        pass

    async def get_answers(
        self,
        comment_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> CommentsResultFromDB:
        pass
