from datetime import datetime

from pydantic import BaseModel

from src.infrastructure.schemas.author import AuthorSchema


class CommentCreateSchema(BaseModel):
    text: str


class CommentReadSchema(BaseModel):
    id: str  # ObjectId
    text: str
    author: AuthorSchema
    post_id: str
    parent_id: str | None
    dislikes: int
    likes: int
    answers_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentsReposeSchema(BaseModel):
    comments: list[CommentReadSchema]
    last_id: str
    has_next: bool


class AnswersReposeSchema(CommentsReposeSchema):
    pass
