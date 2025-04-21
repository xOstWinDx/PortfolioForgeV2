import datetime

from pydantic import BaseModel

from src.infrastructure.schemas.author import AuthorSchema
from src.infrastructure.schemas.comment import CommentsReposeSchema


class PostReadSchema(BaseModel):
    id: str
    title: str
    content: str
    author: AuthorSchema
    dislikes: int
    likes: int
    created_at: datetime.datetime
    comments_count: int
    photos: list[str]

class PostResponseSchema(BaseModel):
    post: PostReadSchema
    recent_comments: CommentsReposeSchema

class PostsResponseSchema(BaseModel):
    posts: PostResponseSchema
    has_next: bool
    last_id: str