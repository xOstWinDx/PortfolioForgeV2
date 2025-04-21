import asyncio
from asyncio import TaskGroup
from typing import NamedTuple

from src.application.interfaces.repo import ICommentsRepository, IPostsRepository
from src.domain.comment import Comment
from src.domain.exceptions import PostNotFoundException
from src.domain.post import Post

class CommentsResultFromService(NamedTuple):
    comments: list[Comment]
    has_next: bool
    last_id: str

class PostResultFromService(NamedTuple):
    post: Post
    recent_comments: CommentsResultFromService

class PostsResultFromService(NamedTuple):
    posts: list[PostResultFromService]
    has_next: bool
    last_id: str


class PostsService:

    def __init__(
            self,
            comments_repo: ICommentsRepository,
            posts_repo: IPostsRepository
    ) -> None:
        self.comments_repo = comments_repo
        self.posts_repo = posts_repo


    async def create_post(self, post: Post) -> Post:
        return await self.posts_repo.create_post(post)

    async def get_post(self, post_id: str) -> PostResultFromService:
        async with TaskGroup() as tg:
            post = tg.create_task(self.posts_repo.get_post(post_id))
            recent_comments = tg.create_task(self.comments_repo.get_comments(post_id, limit=5))
        if not post:
            raise PostNotFoundException(post_id)
        recent_comments=recent_comments.result()
        recent_comments = CommentsResultFromService(
            comments=recent_comments.comments,
            has_next=recent_comments.has_next,
            last_id=recent_comments.comments[-1].id
        )
        return PostResultFromService(post=post.result(), recent_comments=recent_comments)

    async def get_posts(self, last_id: str, limit: int = 20) -> PostsResultFromService:
        posts, has_next = await self.posts_repo.get_posts(last_id, limit)
        last_id = posts.posts[-1].id
        tasks = []
        for post in posts:
            tasks.append(self._load_comments(post))
        post_results: list[PostResultFromService] = await asyncio.gather(*tasks)
        post_results.sort(key=lambda x: x.post.created_at, reverse=True)  # после gather порядок непредсказуем.
        return PostsResultFromService(posts=post_results, has_next=has_next, last_id=last_id)

    async def _load_comments(self, post: Post) -> PostResultFromService:
        comments_has_next = await self.comments_repo.get_comments(post_id=post.id, limit=5)
        recent_comments = CommentsResultFromService(
            comments=comments_has_next.comments,
            has_next=comments_has_next.has_next,
            last_id=comments_has_next.comments[-1].id
        )
        return PostResultFromService(post, recent_comments=recent_comments)

