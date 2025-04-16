from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import ARRAY
from sqlmodel import SQLModel, Field

from src.domain.entities.profile import Profile, JobStatus, SocialLink
from src.domain.entities.project import Project


class ProfileCreate(SQLModel, table=False):
    full_name: str = Field(max_length=50, nullable=False)
    bio: str = Field(max_length=1500, nullable=False)
    location: str = Field(max_length=50, nullable=False)
    experience_summary: str = Field(max_length=150, nullable=False)
    job_status: str = Field(max_length=30, nullable=False)
    resume_link: str = Field(nullable=False, max_length=255)
    social_links: dict[str, str] = Field(sa_type=JSONB, nullable=False)
    skills: list[str] = Field(nullable=False, sa_type=ARRAY(String))  # type: ignore
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)


class ProfileModel(ProfileCreate, table=True):
    __tablename__ = "profiles"
    id: Optional[int] = Field(primary_key=True, default=None)

    @classmethod
    def from_domain(cls, profile: Profile) -> "ProfileModel":
        return cls(
            id=1,  # хардкод, потому что профиль есть только 1 - мой
            full_name=profile.full_name,
            bio=profile.bio,
            location=profile.location,
            experience_summary=profile.experience_summary,
            job_status=profile.job_status.value,
            resume_link=profile.resume_link,
            social_links=profile.social_links,
            skills=profile.skills,
        )

    def to_domain(self) -> Profile:
        return Profile(
            full_name=self.full_name,
            bio=self.bio,
            location=self.location,
            experience_summary=self.experience_summary,
            job_status=JobStatus(self.job_status),
            resume_link=self.resume_link,
            social_links={SocialLink(k): v for k, v in self.social_links.items()},
            skills=self.skills,
            updated_at=self.updated_at,
        )


class ProfileRead(BaseModel):
    full_name: str = Field(max_length=50, nullable=False)
    bio: str = Field(max_length=1500, nullable=False)
    location: str = Field(max_length=50, nullable=False)
    experience_summary: str = Field(max_length=150, nullable=False)
    job_status: str = Field(max_length=30, nullable=False)
    resume_link: str = Field(nullable=False, max_length=255)
    social_links: dict[SocialLink, str] = Field(nullable=False)
    skills: list[str] = Field(nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    class Config:
        from_attributes = True


class ProjectCreate(SQLModel, table=False):
    title: str = Field(max_length=50, nullable=False)
    description: str = Field(max_length=1500, nullable=False)
    role: str = Field(max_length=20, nullable=False)
    technologies: list[str] = Field(nullable=False, sa_type=ARRAY(String))  # type: ignore
    business_goal: str = Field(max_length=150, nullable=False)
    result: str = Field(max_length=150, nullable=False)
    access_note: str = Field(max_length=150, nullable=False)
    is_featured: bool = Field(nullable=False)
    created_at: datetime


class ProjectModel(ProjectCreate, table=True):
    __tablename__ = "projects"
    id: Optional[int] = Field(primary_key=True, default=None)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    technologies: list[str] = Field(nullable=False, sa_type=ARRAY(String))  # type: ignore

    def to_domain(self) -> Project:
        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            role=self.role,
            technologies=self.technologies,
            business_goal=self.business_goal,
            result=self.result,
            access_note=self.access_note,
            is_featured=self.is_featured,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, project: Project) -> "ProjectModel":
        return cls(
            id=project.id,
            title=project.title,
            description=project.description,
            role=project.role,
            technologies=project.technologies,
            business_goal=project.business_goal,
            result=project.result,
            access_note=project.access_note,
            is_featured=project.is_featured,
            created_at=project.created_at,
        )


class ProjectRead(BaseModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    technologies: list[str] = Field(nullable=False)
    title: str = Field(max_length=50, nullable=False)
    description: str = Field(max_length=1500, nullable=False)
    role: str = Field(max_length=20, nullable=False)
    business_goal: str = Field(max_length=150, nullable=False)
    result: str = Field(max_length=150, nullable=False)
    access_note: str = Field(max_length=150, nullable=False)
    is_featured: bool = Field(nullable=False)
    created_at: datetime

    class Config:
        from_attributes = True
