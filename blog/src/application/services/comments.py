from asyncio import TaskGroup

from src.application.interfaces.repo import IUserRepository, IPostsRepository
from src.application.interfaces.repo import ICommentsRepository
from src.application.services.results import CommentsResultFromService
from src.domain.comment import Comment
from src.domain.exceptions import (
    UserNotFoundException,
    PostNotFoundException,
    CommentNotFoundException,
)


class CommentsService:
    def __init__(
        self,
        comments_repo: ICommentsRepository,
        users_repo: IUserRepository,
        posts_repo: IPostsRepository,
    ) -> None:
        self.comments_repo = comments_repo
        self.users_repo = users_repo
        self.posts_repo = posts_repo

    async def create(self, comment: Comment, user_id: int) -> Comment:
        """Создаёт комментарий или ответ на комментарий"""
        is_answer = bool(comment.parent_id)
        async with TaskGroup() as tg:
            author_task = tg.create_task(self.users_repo.get_by_id(user_id))
            post_task = tg.create_task(self.posts_repo.get_one(comment.post_id))
            if is_answer:
                comment_task = tg.create_task(
                    self.comments_repo.get_one(comment.parent_id)
                )
        author = author_task.result()
        post = post_task.result()
        parent_exists = comment_task.result() if is_answer else True

        if not author:
            raise UserNotFoundException(user_id)
        if not post:
            raise PostNotFoundException(comment.post_id)
        if not parent_exists:
            raise CommentNotFoundException(comment.parent_id)

        comment.author = author
        return await self.comments_repo.create(comment)

    async def get(
        self, post_id: str, parent_id: str | None, last_id: str | None, limit: int = 10
    ) -> CommentsResultFromService:
        res_from_db = await self.comments_repo.get_many(
            post_id=post_id, comment_id=parent_id, last_id=last_id, limit=limit
        )
        return CommentsResultFromService(
            comments=res_from_db.comments,
            has_next=res_from_db.has_next,
            last_id=res_from_db.comments[-1].id,
        )

    async def like(self, comment_id: str, user_id: int) -> bool:
        if not await self.comments_repo.get_one(comment_id):
            raise CommentNotFoundException(comment_id)
        return await self.comments_repo.like(comment_id, user_id)  # type: ignore

    async def dislike(self, comment_id: str, user_id: int) -> bool:
        if not await self.comments_repo.get_one(comment_id):
            raise CommentNotFoundException(comment_id)
        return await self.comments_repo.dislike(comment_id, user_id)  # type: ignore
