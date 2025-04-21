from datetime import datetime
from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    NOT_LOOKING = "NOT_LOOKING"  # Не ищу работу
    PASSIVELY_LOOKING = "PASSIVELY_LOOKING"  # Пассивно ищу (рассматриваю варианты)
    ACTIVELY_LOOKING = "ACTIVELY_LOOKING"  # Активно ищу работу


class SocialLink(StrEnum):
    VK = "VK"
    TELEGRAM = "TELEGRAM"
    GITHUB = "GITHUB"


# Пошаговые схемы для профиля
class FullNameSchema(BaseModel):
    full_name: str = Field(..., max_length=50)


class BioSchema(BaseModel):
    bio: str = Field(..., max_length=1500)


class LocationSchema(BaseModel):
    location: str = Field(..., max_length=50)


class ExperienceSummarySchema(BaseModel):
    experience_summary: str = Field(..., max_length=150)


class JobStatusSchema(BaseModel):
    job_status: JobStatus


class ResumeLinkSchema(BaseModel):
    resume_link: str = Field(..., max_length=255)


class SocialLinksSchema(BaseModel):
    social_links: dict[SocialLink, str]


class SkillsSchema(BaseModel):
    skills: list[str]


# Полная схема профиля
class ProfileSchema(BaseModel):
    full_name: str
    bio: str
    location: str
    experience_summary: str
    job_status: str
    resume_link: str
    social_links: dict[str, str]
    skills: list[str]


# Пошаговые схемы для проекта
# src/presentation/telegram/schemas.py (продолжение)
class TitleSchema(BaseModel):
    title: str = Field(..., max_length=50)


class DescriptionSchema(BaseModel):
    description: str = Field(..., max_length=1500)


class RoleSchema(BaseModel):
    role: str = Field(..., max_length=20)


class TechnologiesSchema(BaseModel):
    technologies: list[str]


class BusinessGoalSchema(BaseModel):
    business_goal: str = Field(..., max_length=150)


class ResultSchema(BaseModel):
    result: str = Field(..., max_length=150)


class AccessNoteSchema(BaseModel):
    access_note: str = Field(..., max_length=150)


class IsFeaturedSchema(BaseModel):
    is_featured: bool


# Полная схема проекта
class ProjectSchema(BaseModel):
    title: str
    description: str
    role: str
    technologies: List[str]
    business_goal: str
    result: str
    access_note: str
    is_featured: bool
    created_at: datetime
