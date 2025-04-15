import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

import httpx
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
from starlette.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    """Предзагружаем OpenAPI-схемы при старте."""
    app.openapi_schema = await preload_openapi_schemas()
    yield


# Минимальная настройка FastAPI
app = FastAPI(
    docs_url="",
    openapi_url="",
    title="PortfolioForge API",
    description=(
        "## PortfolioForge API\n\n"
        "Единая документация для всех микросервисов.\n\n"
        "### Контакты\n"
        "- **Связаться**: [Telegram](https://t.me/m/zvhobMxSNGQy)\n"
        "- **Email**: [Starobogatov.alexey@gmail.com](mailto:Starobogatov.alexey@gmail.com)"
    ),
    version="1.0.0",
    lifespan=life_span,
)

# Конфигурация микросервисов
MICROSERVICES = {
    "auth": {
        "dev_url": "http://localhost:8001/openapi.json",
        "prod_url": "http://auth:8001/openapi.json",
        "description": "Сервис авторизации для работы с пользователями и токенами.",
    },
}

# Определяем среду
PROD = os.getenv("PROD", "false").lower() == "true"
BASE_URL = os.getenv("API_BASE_URL", "https://localhost:8080")


async def fetch_openapi_schema(url: str) -> Dict[str, Any]:
    """Запрашивает OpenAPI-схему по URL."""
    logger.info(f"Fetching schema from {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            response.raise_for_status()
            return response.json()  # type: ignore
        except Exception as e:
            logger.error(f"Failed to fetch schema from {url}: {e}")
            return {}


def merge_openapi_schemas(schemas: list[tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Объединяет OpenAPI-схемы в одну плоскую структуру."""
    # Базовая схема от FastAPI
    merged_schema = app.openapi()

    # Добавляем единый сервер
    merged_schema["servers"] = [
        {"url": BASE_URL, "description": "Unified API endpoint"}
    ]

    # Инициализируем теги и компоненты, если их нет
    if "tags" not in merged_schema:
        merged_schema["tags"] = []
    if "components" not in merged_schema:
        merged_schema["components"] = {"schemas": {}, "securitySchemes": {}}

    # Множество существующих тегов для избежания дублирования
    existing_tags = {tag["name"] for tag in merged_schema["tags"]}

    for service_name, schema in schemas:
        if not schema:
            logger.warning(f"No valid schema for {service_name}")
            continue

        # Объединяем пути
        for path, methods in schema.get("paths", {}).items():
            # Удаляем префиксы для плоской структуры
            normalized_path = f"/{path.lstrip('/api').lstrip('/')}"
            if normalized_path not in merged_schema["paths"]:
                merged_schema["paths"][normalized_path] = {}

            for method, details in methods.items():
                updated_details = details.copy()
                # Сохраняем исходные теги или добавляем тег сервиса
                if "tags" not in updated_details or not updated_details["tags"]:
                    service_tag = {
                        "name": service_name,
                        "description": MICROSERVICES[service_name]["description"],
                    }
                    if service_name not in existing_tags:
                        merged_schema["tags"].append(service_tag)
                        existing_tags.add(service_name)
                    updated_details["tags"] = [service_name]
                merged_schema["paths"][normalized_path][method] = updated_details

        # Объединяем компоненты
        if "components" in schema:
            for component_type in ["schemas", "securitySchemes"]:
                for key, value in schema["components"].get(component_type, {}).items():
                    if key not in merged_schema["components"][component_type]:
                        merged_schema["components"][component_type][key] = value

        # Добавляем теги из исходной схемы
        if "tags" in schema:
            for tag in schema["tags"]:
                if tag["name"] not in existing_tags:
                    merged_schema["tags"].append(tag)
                    existing_tags.add(tag["name"])

    return merged_schema  # type: ignore


@app.get("/openapi.json", include_in_schema=False)
async def get_unified_openapi() -> dict[str, Any]:
    """Возвращает объединённую OpenAPI-схему."""
    schemas = []
    tasks = [
        fetch_openapi_schema(config["prod_url" if PROD else "dev_url"])
        for config in MICROSERVICES.values()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for (service_name, _), schema in zip(MICROSERVICES.items(), results):
        if isinstance(schema, dict):
            schemas.append((service_name, schema))
        else:
            logger.error(f"Failed to load schema for {service_name}")

    return merge_openapi_schemas(schemas)


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def get_documentation() -> HTMLResponse:
    """Отдаёт Swagger UI с объединённой документацией."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="PortfolioForge API",
        redoc_favicon_url="https://42812a87-8640-4d3e-a250-8550c4a8ce16.selstorage.ru/doc.logo.png",
    )


async def preload_openapi_schemas() -> Dict[str, Any]:
    """Предзагружает схемы при старте."""
    schemas = []
    tasks = [
        fetch_openapi_schema(config["prod_url" if PROD else "dev_url"])
        for config in MICROSERVICES.values()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for (service_name, _), schema in zip(MICROSERVICES.items(), results):
        if isinstance(schema, dict):
            schemas.append((service_name, schema))
        else:
            logger.warning(f"Failed to preload schema for {service_name}")

    return merge_openapi_schemas(schemas)


@app.get("/health", status_code=200, include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
