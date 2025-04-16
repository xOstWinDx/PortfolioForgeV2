from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Project:
    id: int | None
    title: str
    description: str
    role: str
    technologies: list[str]
    business_goal: str
    result: str
    access_note: str
    is_featured: bool
    created_at: datetime
    updated_at: datetime | None
