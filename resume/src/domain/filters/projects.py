from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectsFilter:
    id: int | None = None
    is_featured: bool | None = None
