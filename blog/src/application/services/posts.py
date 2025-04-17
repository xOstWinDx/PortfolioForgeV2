from src.application.interfaces.repo import (
    ICommentsRepository,
    IPostsRepository,
    PostsResult,
)
from src.domain.comment import Comment
from src.domain.exceptions import PostNotFoundException
from src.domain.post import Post


class PostsService:
    def __init__(
        self, comments_repo: ICommentsRepository, posts_repo: IPostsRepository
    ) -> None:
        self.comments_repo = comments_repo
        self.posts_repo = posts_repo

    async def create_post(self, post: Post) -> Post:
        return await self.posts_repo.create_post(post)

    async def get_post(self, post_id: str) -> tuple[Post, list[Comment]]:
        res = await self.posts_repo.get_post(post_id)
        if not res:
            raise PostNotFoundException(post_id)
        return res  # type: ignore

    async def get_posts(
        self, last_id: str | None = None, limit: int = 20
    ) -> PostsResult:
        return await self.posts_repo.get_posts(last_id, limit)
