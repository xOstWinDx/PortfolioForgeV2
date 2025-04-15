from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    """
    Генерирует кастомную OpenAPI-схему.

    Args:
        app: FastAPI приложение.

    Returns:
        Dict[str, Any]: Обновлённая OpenAPI-схема.
    """
    # Получаем базовую OpenAPI-схему
    openapi_schema = get_openapi(
        title=app.title,  # noqa
        summary=app.summary,  # noqa
        version=app.version,  # noqa
        description=app.description,  # noqa
        routes=app.routes,
        servers=app.servers,  # noqa
        tags=app.openapi_tags,  # noqa
    )
    # В этом сервисе локальная и продакшн документация совпадают.
    return openapi_schema  # type: ignore
