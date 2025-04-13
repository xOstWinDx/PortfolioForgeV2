import base64
import io
from datetime import datetime
from typing import Any, Annotated

from PIL import Image
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi.params import Cookie, File
from fastapi_cache.decorator import cache
from starlette.responses import JSONResponse

from src.application.services.auth import AuthService
from src.application.services.user import UserService
from src.config import settings
from src.domain.credentials import AuthenticateCredentials
from src.domain.exceptions import UnauthorizedError
from src.domain.user import User, RolesEnum
from src.infrastructure.models import (
    RegisterUserSchema,
    UserReadSchema,
    LoginUserSchema,
)
from src.infrastructure.s3 import S3Client
from src.presentation.http.dependencies import (
    get_user_service,
    get_auth_service,
    get_current_user,
    get_s3_client,
)
from src.presentation.http.schema import CredentialsSchema
from src.utils.images.prepare import process_image_to_webp

router = APIRouter(prefix="/auth")

jwks = Annotated[dict[str, list[dict[str, Any]]], 200]


@router.get("/.well-known/jwks.json", status_code=200)
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


@router.post("/register", status_code=201)
async def register(
    user_form_data: RegisterUserSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserReadSchema:
    user = await user_service.create_user(user_form_data.to_domain())
    return UserReadSchema.model_validate(user, from_attributes=True)


@router.post("/login", status_code=200, response_model=CredentialsSchema)
async def login(
    login_form_data: LoginUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    credentials = await auth_service.login(
        email=str(login_form_data.email), password=login_form_data.password
    )
    res = {
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


@router.post("/refresh", status_code=200, response_model=CredentialsSchema)
async def refresh(
    refresh_token: Annotated[str, Cookie(include_in_schema=False)],
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    credentials = await auth_service.refresh(AuthenticateCredentials(refresh_token))
    res = {
        "access_token": credentials[0].read(),
        "refresh_token": credentials[1].read(),
    }
    response = JSONResponse(content=res)
    response.set_cookie(
        key="access_token",
        value=res["access_token"],
        max_age=settings.ACCESS_TOKEN_EXPIRES,
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


@router.get("/users/me", status_code=200)
@cache(expire=180)
async def get_me(user: User = Depends(get_current_user)) -> UserReadSchema:
    return UserReadSchema.model_validate(user, from_attributes=True)


@router.patch("/users/{user_id}/photo", status_code=200)
async def change_photo(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
    file: UploadFile = File(
        description="Upload image (JPEG, PNG, WEBP)", media_type="image/*"
    ),
    s3_client: S3Client = Depends(get_s3_client),
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

        # Проверка типа
        if file.content_type not in settings.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid MIME type")
        try:
            Image.open(file_content).verify()  # Проверяет, что это изображение
        except Exception:
            raise HTTPException(status_code=400, detail="File is not a valid image")
        await file.seek(0)  # Сбрасываем позицию для дальнейшей обработки

        file_content, file_extension = process_image_to_webp(file_obj=file_content)

        # Формируем имя файла
        file_key = f"profiles/{user_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{file_extension}"

        # Загружаем в S3
        result = await s3_client.upload_file(
            file_obj=file_content, file_key=file_key, content_type=file.content_type
        )

        # Обновляем данные пользователя
        user.photo_url = result["file_url"]
        res = await user_service.update_user(user)

        return UserReadSchema.model_validate(res, from_attributes=True)

    raise UnauthorizedError("You are not allowed to change this user's photo")
