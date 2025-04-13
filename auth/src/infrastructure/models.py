from typing import Annotated, Optional

from fastapi import Form
from password_strength import PasswordPolicy
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship

from src.domain.user import User, RolesEnum
from src.infrastructure.pwd_hash import hash_password

policy = PasswordPolicy.from_names(
    length=8,  # Мин. Длинна 8
    uppercase=1,  # 1 Заглавная
    numbers=1,  # 1 Цифра
    special=1,  # 1 Спецсимвол
)


class RoleModel(SQLModel, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=20, nullable=False, unique=True)


class LoginUserSchema(SQLModel, table=False):
    email: Annotated[EmailStr, Form(max_length=50, min_length=2)]
    password: Annotated[str, Form(max_length=64, min_length=8)]


class RegisterUserSchema(LoginUserSchema, table=False):
    username: Annotated[str, Form(max_length=20, min_length=6)]

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        errors = policy.test(value)
        if errors:
            raise ValueError(f"Password too weak: {', '.join(str(e) for e in errors)}")
        return value

    def to_domain(self) -> User:
        return User(
            id=None,
            email=str(self.email),
            username=self.username,
            role=RolesEnum.USER,
            password=hash_password(self.password),
        )


class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(primary_key=True, default=None)
    email: str = Field(max_length=50, index=True, unique=True, nullable=False)
    username: str = Field(max_length=20, min_length=6)
    hashed_password: bytes = Field(nullable=False)
    role_id: int = Field(nullable=False, foreign_key="roles.id")
    role: RoleModel = Relationship(sa_relationship_kwargs={"lazy": "joined"})

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
        )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            role=RolesEnum(self.role.name),
            password=self.hashed_password,
        )


class UserReadSchema(SQLModel, table=False):
    id: int
    email: EmailStr
    username: str
    role: str
