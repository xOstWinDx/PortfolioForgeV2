from fastapi import APIRouter, Depends, Query
from starlette import status

from src.application.services.posts import PostsService
from src.infrastructure.schemas.exceptions import ExceptionSchema, ValidationErrorSchema
from src.infrastructure.schemas.post import PostResponseSchema, PostsResponseSchema
from src.presentation.api.dependencies import get_posts_service

router = APIRouter(prefix="/posts")


@router.get(
    path="/{post_id}",
    summary="Получить пост",
    status_code=status.HTTP_200_OK,
    response_model=PostResponseSchema,
    responses={
        200: {"description": "Успешное получение поста"},
        404: {
            "description": "Пост не найден", "content":
                {"application/json":
                     {"schema": ExceptionSchema.model_json_schema()}
                 }
        },
        422: {
            "description": "Ошибка валидации входных данных",
            "content": {"application/json": {"schema": ValidationErrorSchema.model_json_schema()}}
        }
    }
)
async def get_post_by_id(
    post_id: str,
    posts_service: PostsService = Depends(get_posts_service),
):
    return await posts_service.get_post(post_id)


@router.get(
    path="/",
    summary="Получить список постов",
    status_code=status.HTTP_200_OK,
    response_model=PostsResponseSchema,
    responses={
        200: {"description": "Успешное получение списка постов"},
        422: {
            "description": "Ошибка валидации входных данных",
            "content": {"application/json": {"schema": ValidationErrorSchema.model_json_schema()}}
        }
    }
)
async def get_posts(
    last_id: str | None,
    limit: Query(le=20, default=10, ge=1),
    posts_service: PostsService = Depends(get_posts_service),
):
    return await posts_service.get_posts(last_id, limit)

# TODO: Лайк / Дизлайк постов

# TODO: Комментарии workflow











