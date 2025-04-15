import base64
import io
import logging
from typing import Any, Annotated

from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi.params import File
from fastapi_cache.decorator import cache
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.application.interfaces.uow import AbstractUnitOfWork
from src.application.services.auth import AuthService
from src.application.services.image import ImageService
from src.application.services.user import UserService
from src.config import settings
from src.domain.credentials import AuthenticateCredentials
from src.domain.exceptions import AuthenticationError, AuthorizationError
from src.domain.user import User, RolesEnum
from src.infrastructure.entities.schemas import (
    LoginUserSchema,
    UserReadSchema,
    CredentialsSchema,
    RegisterUserForm,
)
from src.presentation.http.dependencies import (
    get_user_service,
    get_auth_service,
    get_current_user,
    get_image_service,
    get_uow,
)
from src.presentation.http.docs.description import RETURN_TOKENS, REFRESH_COOKIE_NOTE
from src.presentation.http.docs.responses import ResponsesEnum

router = APIRouter()

jwks = Annotated[dict[str, list[dict[str, Any]]], 200]

logger = logging.getLogger(__name__)


@router.get("/.well-known/jwks.json", status_code=200, include_in_schema=False)
@cache(expire=60 * 60 * 24 * 7)  # 7 days
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
    return response


@router.post(
    "/register",
    status_code=201,
    summary="Регистрация",
    responses={
        409: ResponsesEnum.R_409,
        201: {"description": "Пользователь успешно зарегистрирован"},
        422: ResponsesEnum.R_422,
    },
    tags=["Authentication"],
)
async def register(
    user_form_data: Annotated[RegisterUserForm, Depends()],
    uow: AbstractUnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> UserReadSchema:
    async with uow:
        user = await user_service.create_user(user_form_data.model.to_domain(), uow)
        await uow.commit()
    return UserReadSchema.model_validate(user, from_attributes=True)


@router.post(
    "/login",
    status_code=200,
    summary="Авторизоваться",
    description=(f"{RETURN_TOKENS}"),
    responses={
        200: {"description": "Успешная авторизация"},
        401: ResponsesEnum.R_401,
        422: ResponsesEnum.R_422,
    },
    response_model=CredentialsSchema,
    tags=["Authentication"],
)
async def login(
    form_data: Annotated[LoginUserSchema, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    credentials = await auth_service.login(
        email=str(form_data.email), password=form_data.password
    )
    res = {"access_token": credentials[0].read()}
    response = JSONResponse(content=res)
    response.set_cookie(
        key="refresh_token",
        value=credentials[1].read(),
        max_age=settings.REFRESH_TOKEN_EXPIRES,
        httponly=True,
    )
    return response


@router.post(
    "/refresh",
    status_code=200,
    summary="Обновить токены",
    description=(f"{REFRESH_COOKIE_NOTE}\n{RETURN_TOKENS}"),
    responses={
        401: ResponsesEnum.R_401,
        200: {
            "description": "Успешное обновление токенов",
        },
    },
    response_model=CredentialsSchema,
    tags=["Authentication"],
)
async def refresh(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning(
            f"Refresh token not found, cookies: {request.cookies.keys()}",
        )
        raise AuthenticationError("Refresh token not found")
    credentials = await auth_service.refresh(AuthenticateCredentials(refresh_token))
    res = {
        "access_token": credentials[0].read(),
    }
    response = JSONResponse(content=res)
    response.set_cookie(
        key="refresh_token",
        value=credentials[1].read(),
        max_age=settings.REFRESH_TOKEN_EXPIRES,
        httponly=True,
    )
    return response


@router.post(
    "/logout",
    status_code=204,
    summary="Выход",
    description=(f"{REFRESH_COOKIE_NOTE}"),
    responses={
        204: {
            "description": "Успешное выход из аккаунта",
        }
    },
    tags=["Authentication"],
)
async def logout() -> JSONResponse:
    res = {"status": "success"}
    response = JSONResponse(content=res)
    response.delete_cookie(key="refresh_token")
    return response


@router.get(
    "/users/me",
    status_code=200,
    summary="Профиль",
    responses={
        200: {"description": "Успешное получение информации о текущем пользователе"},
        401: ResponsesEnum.R_401,
        404: ResponsesEnum.R_404,
    },
    response_model=UserReadSchema,
    tags=["Users"],
)
@cache(expire=180)
async def get_me(user: User = Depends(get_current_user)) -> UserReadSchema:
    return UserReadSchema.model_validate(user, from_attributes=True)


@router.patch(
    "/users/{user_id}/photo",
    status_code=200,
    summary="Изменить аватар пользователя",
    responses={
        200: {"description": "Успешное изменение фотографии пользователя"},
        401: ResponsesEnum.R_401,
        404: ResponsesEnum.R_404,
        403: ResponsesEnum.R_403,
        422: ResponsesEnum.R_422,
    },
    response_model=UserReadSchema,
    tags=["Users"],
)
async def change_photo(
    user_id: int,
    file: UploadFile = File(
        ..., description="Фотография в формате: (JPEG, PNG, WEBP)", media_type="image/*"
    ),
    uow: AbstractUnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service),
) -> UserReadSchema:
    if user_id == user.id or user.role >= RolesEnum.MODERATOR:
        # Проверка размера
        file_size = 0
        file_content = io.BytesIO()
        while chunk := await file.read(1024):
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large, max size is {settings.MAX_FILE_SIZE / 1024 / 1024}MB",
                )
            file_content.write(chunk)
        # Сбросить позицию для дальнейшего чтения
        await file.seek(0)

        # Валидация расширения
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in {"webp", "jpg", "jpeg", "png"}:
            raise HTTPException(status_code=400, detail="Invalid file extension")

        async with uow:
            avatar = await image_service.add(file_content, uow)
            user.avatar = avatar
            res = await user_service.update_user(user, uow)
            await uow.commit()

        return UserReadSchema.model_validate(res, from_attributes=True)

    raise AuthorizationError("You are not allowed to change this user's photo")
