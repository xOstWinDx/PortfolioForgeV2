from abc import ABC, abstractmethod
from typing import Literal, NamedTuple

from src.domain.author import Author
from src.domain.comment import Comment
from src.domain.post import Post


class PostsResultFromDB(NamedTuple):
    posts: list[Post]
    has_next: bool


class CommentsResultFromDB(NamedTuple):
    comments: list[Comment]
    has_next: bool


class IPostsRepository(ABC):
    @abstractmethod
    async def get_one(self, post_id: str) -> Post | None:
        raise NotImplementedError

    @abstractmethod
    async def get_many(
        self,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc",
    ) -> PostsResultFromDB:
        raise NotImplementedError

    @abstractmethod
    async def create(self, post: Post) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def like(self, post_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike(self, post_id: str, user_id: int) -> bool:
        raise NotImplementedError


class ICommentsRepository(ABC):
    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, comment_id: str) -> Comment | None:
        raise NotImplementedError

    @abstractmethod
    async def like(self, comment_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike(self, comment_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_many(
        self,
        post_id: str,
        comment_id: str | None = None,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> CommentsResultFromDB:
        raise NotImplementedError


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: Author) -> Author:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, user_email: str) -> Author | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Author | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: Author) -> Author:
        raise NotImplementedError
