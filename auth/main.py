from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aio_pika
from fastapi import FastAPI, HTTPException
from starlette import status
from starlette.requests import Request

from src.config import settings
from src.domain.exceptions import ConflictError
from src.presentation.http.router import router


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
    yield
    await connection.close()


app = FastAPI(title="Auth Service", version="0.0.1", lifespan=life_span)

app.include_router(router)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
