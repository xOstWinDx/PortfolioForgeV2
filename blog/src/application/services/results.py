from typing import NamedTuple

from src.domain.comment import Comment
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
