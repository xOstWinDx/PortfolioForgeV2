from typing import Annotated

from fastapi import Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, field_validator, model_validator, BaseModel
from sqlmodel import SQLModel

from src.config import settings, policy
from src.domain.user import User, RolesEnum, Avatar
from src.infrastructure.pwd_hash import hash_password
from src.presentation.http.docs.description import PASSWORD_REQUIRED


class LoginUserSchema(OAuth2PasswordRequestForm):
    def __init__(
        self, *, username: Annotated[EmailStr, Form()], password: Annotated[str, Form()]
    ):
        super().__init__(username=str(username), password=password)

        self.email = str(username).lower()

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_user@example.com",
                "password": "!StrongP@ssword123",
            }
        }


class RegisterUserForm:
    def __init__(
        self,
        username: str = Form(..., min_length=6, max_length=20),
        email: EmailStr = Form(..., min_length=2, max_length=50),
        password: str = Form(
            ..., min_length=8, max_length=64, description=PASSWORD_REQUIRED
        ),
    ):
        self.model = RegisterUserSchema(
            username=username, email=email, password=password
        )


class RegisterUserSchema(SQLModel, table=False):
    username: Annotated[str, Form(max_length=20, min_length=6)]
    email: Annotated[EmailStr, Form(max_length=50, min_length=2)]
    password: Annotated[
        str, Form(max_length=64, min_length=8, description=PASSWORD_REQUIRED)
    ] = Depends()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "NewUser@example.com",
                "password": "StrongP@ssword123",
                "username": "NewUser",
            }
        }

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        errors = policy.test(value)
        if errors:
            raise ValueError(f"Password too weak: {', '.join(str(e) for e in errors)}")
        return value

    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.lower()

    def to_domain(self) -> User:
        return User(
            id=None,
            email=str(self.email),
            username=self.username,
            role=RolesEnum.USER,
            password=hash_password(self.password),
            avatar=Avatar(id="default", file_url=settings.DEFAULT_PHOTO_URL),
        )


class UserReadSchema(SQLModel, table=False):
    id: int
    email: EmailStr
    username: str
    role: RolesEnum
    photo_url: str

    @model_validator(mode="before")
    def validate_photo_url(cls, values: User) -> User:
        values.photo_url = values.avatar.file_url
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "NewUser@example.com",
                "username": "NewUser",
                "role": "USER",
                "photo_url": "https://42812a87-8640-4d3e-a250-8550c4a8ce16.selstorage.ru/profiles/default.webp",
            }
        }


class CredentialsSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
            }
        }
