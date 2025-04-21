from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

from src.domain.user import User, RolesEnum, Avatar
from src.infrastructure.pwd_hash import hash_password


class RoleModel(SQLModel, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=20, nullable=False, unique=True)


class ImageModel(SQLModel, table=True):
    __tablename__ = "images"
    id: str = Field(primary_key=True)
    file_url: str = Field(nullable=False, unique=True)


class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(primary_key=True, default=None)
    email: str = Field(max_length=50, index=True, unique=True, nullable=False)
    username: str = Field(max_length=20, min_length=6)
    hashed_password: bytes = Field(nullable=False)
    role_id: int = Field(nullable=False, foreign_key="roles.id")
    avatar_id: str = Field(nullable=True, foreign_key="images.id")

    role: RoleModel = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    avatar: ImageModel = Relationship(sa_relationship_kwargs={"lazy": "joined"})

    @field_validator("hashed_password", mode="before")
    @classmethod
    def validate_password(cls, value: str | bytes) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return hash_password(value)  # type: ignore
        raise ValueError(
            f"Invalid password type expected bytes or str got {type(value)}"
        )

    @classmethod
    def from_domain(cls, user: User, role_id: int) -> "UserModel":
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.password,
            role_id=role_id,
            avatar_id=user.avatar.id,
        )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            role=RolesEnum(self.role.name),
            password=self.hashed_password,
            avatar=Avatar(id=self.avatar.id, file_url=self.avatar.file_url),
        )
