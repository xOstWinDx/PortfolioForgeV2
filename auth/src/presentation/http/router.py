import base64
from typing import Any, Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from src.application.services.auth import AuthService
from src.application.services.user import UserService
from src.config import settings
from src.infrastructure.models import (
    RegisterUserSchema,
    UserReadSchema,
    LoginUserSchema,
)
from src.presentation.http.dependencies import get_user_service, get_auth_service

router = APIRouter(prefix="/auth")

jwks = Annotated[dict[str, list[dict[str, Any]]], 200]


@router.get("/.well-known/jwks.json", status_code=200)
async def get_jwks() -> JSONResponse:
    public_numbers = settings.PUBLIC_KEY.public_numbers()
    res: jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": settings.CURRENT_KID,
                "use": "sig",
                "alg": "RS256",
                "n": base64.urlsafe_b64encode(
                    public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8)
                )
                .decode()
                .rstrip("="),
                "e": base64.urlsafe_b64encode(
                    public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8)
                )
                .decode()
                .rstrip("="),
            }
        ]
    }

    response = JSONResponse(content=res)
    response.headers["Cache-Control"] = "max-age=86400"  # 24 hours
    return response


@router.post("/register", status_code=201)
async def register(
    user_form_data: RegisterUserSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserReadSchema:
    user = await user_service.create_user(user_form_data.to_domain())
    return UserReadSchema.model_validate(user, from_attributes=True)


@router.post("/login", status_code=200)
async def login(
    login_form_data: LoginUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    credentials = await auth_service.login(
        email=str(login_form_data.email), password=login_form_data.password
    )
    res = {
        "status": "success",
        "access_token": credentials[0].read(),
        "refresh_token": credentials[1].read(),
    }
    response = JSONResponse(content=res)
    response.set_cookie(
        key="access_token",
        value=credentials[0].read(),
        max_age=settings.ACCESS_TOKEN_EXPIRES,
        httponly=True,
    )
    response.set_cookie(
        key="refresh_token",
        value=credentials[1].read(),
        max_age=settings.REFRESH_TOKEN_EXPIRES,
        secure=True,
        httponly=True,
    )
    return response


@router.post("/logout", status_code=200)
async def logout() -> JSONResponse:
    res = {"status": "success"}
    response = JSONResponse(content=res)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
