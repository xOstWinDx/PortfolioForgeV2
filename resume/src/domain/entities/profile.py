from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JobStatus(StrEnum):
    NOT_LOOKING = "NOT_LOOKING"  # Не ищу работу
    PASSIVELY_LOOKING = "PASSIVELY_LOOKING"  # Пассивно ищу (рассматриваю варианты)
    ACTIVELY_LOOKING = "ACTIVELY_LOOKING"  # Активно ищу работу


class SocialLink(StrEnum):
    VK = "VK"
    TELEGRAM = "TELEGRAM"
    GITHUB = "GITHUB"


@dataclass(frozen=True)
class Profile:
    full_name: str
    bio: str
    location: str
    experience_summary: str
    job_status: JobStatus
    resume_link: str
    social_links: dict[SocialLink, str]
    skills: list[str]
    updated_at: datetime
