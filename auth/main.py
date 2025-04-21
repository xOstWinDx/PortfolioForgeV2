import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import aio_pika
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.config import settings
from src.domain.exceptions import ConflictError, AuthenticationError, AuthorizationError, ValidationError
from src.infrastructure.exceptions import S3ClientException
from src.presentation.http.docs.openapi import custom_openapi
from src.presentation.http.router import router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, timeout=10)
    app.state.connection = connection  # noqa
    redis = aioredis.from_url(settings.REDIS_URL)
    backend = RedisBackend(redis)
    await backend.redis.ping()
    FastAPICache.init(
        backend,
        prefix="auth_service",
        cache_status_header="X-Cache-Status",
    )
    yield
    await connection.close()


app = FastAPI(
    title="Auth Service",
    version="0.0.1",
    openapi_url="",
    docs_url="",
    redoc_url="",
    summary="API для управления пользователями и авторизацией.",
    description=(
        "## Описание сервиса\n\n"
        "Микросервис для управления пользователями и авторизацией. "
        "Предоставляет endpoints для регистрации, входа, обновления токенов и работы с профилем.\n\n"
        "### Ключевые особенности\n"
        "- **Авторизация**: OAuth2 Bearer токены через заголовок `Authorization: Bearer <token>`.\n"
        "- **Валидация**: Все данные проверяются через Pydantic.\n"
        "- **Кэширование**: Некоторые endpoints оптимизированы с помощью кэша. \n\n"
        "### Связаться\n"
        "- Telegram: [API Developer](https://t.me/m/zvhobMxSNGQy)\n"
        "- Email: [Starobogatov.alexey@gmail.com](mailto:Starobogatov.alexey@gmail.com)"
    ),
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints для работы с авторизацией.",
        },
        {
            "name": "Users",
            "description": "Endpoints для работы с пользователями.",
        },
    ],
    lifespan=life_span,
)

app.include_router(router)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@app.exception_handler(AuthenticationError)
async def unauthorized_handler(request: Request, exc: AuthenticationError) -> None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.exception_handler(S3ClientException)
async def s3_client_exception_handler(request: Request, exc: S3ClientException) -> None:
    HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to upload file",
    )


@app.exception_handler(AuthorizationError)
async def forbidden_handler(request: Request, exc: AuthorizationError) -> None:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json() -> dict[str, Any]:
    return custom_openapi(app)  # type: ignore


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> dict[str, Any]:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def get_documentation() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Auth Service API Documentation",
        swagger_favicon_url="https://42812a87-8640-4d3e-a250-8550c4a8ce16.selstorage.ru/doc.logo.png",
    )
    # return get_redoc_html(
    #     openapi_url="/openapi.json",
    #     title="Auth Service API Documentation",
    #     redoc_favicon_url="https://42812a87-8640-4d3e-a250-8550c4a8ce16.selstorage.ru/doc.logo.png"
    # )


@app.get("/health", status_code=200, include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
