import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aio_pika
from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette import status
from starlette.requests import Request

from src.config import settings
from src.domain.exceptions import ConflictError, UnauthorizedError
from src.infrastructure.exceptions import S3ClientException
from src.presentation.http.router import router

logging.basicConfig(level=logging.INFO)


# ────────────────
# TODO [12.04.2025 | High]
# Assigned to: stark
# Description: Реализовать
# Steps:
#   - Генерацию JWT
#   - Аутентификацию Пользователя
#   - Переиздание токенов
#   - BLACKLIST токенов *и возможно WHITELIST*
# ────────────────
@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    app.state.connection = connection
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


app = FastAPI(title="Auth Service", version="0.0.1", lifespan=life_span)

app.include_router(router)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.exception_handler(S3ClientException)
async def s3_client_exception_handler(request: Request, exc: S3ClientException) -> None:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to upload file",
    )
