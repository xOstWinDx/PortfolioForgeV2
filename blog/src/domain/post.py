from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Any, Optional

from src.domain.author import Author


@dataclass
class Post:
    id: str # ObjectID
    title: str
    content: str
    author: Optional[Author]  # В момент создания поста нет полных данных автора.
    dislikes: int
    likes: int
    created_at: datetime
    comments_count: int
    images: list[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        _id = data.get("id") or data.get("_id")
        return cls(
            id=_id,
            title=data.get("title"),
            content=data.get("content"),
            author=data.get("author"),
            dislikes=data.get("dislikes"),
            likes=data.get("likes"),
            created_at=data.get("created_at"),
            comments_count=data.get("comments_count"),
            images=data.get("images"),
        )
