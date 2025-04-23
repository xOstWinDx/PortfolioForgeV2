from fastapi import APIRouter, Depends, Query, Header, HTTPException
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
            "description": "Пост не найден",
            "content": {
                "application/json": {"schema": ExceptionSchema.model_json_schema()}
            },
        },
        422: {
            "description": "Ошибка валидации входных данных",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
    tags=["Posts"],
)
async def get_post_by_id(
    post_id: str,
    posts_service: PostsService = Depends(get_posts_service),
) -> PostsResponseSchema:
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
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
    tags=["Posts"],
)
async def get_posts(
    last_id: str | None,
    limit: int = Query(le=20, default=10, ge=1),
    posts_service: PostsService = Depends(get_posts_service),
) -> PostsResponseSchema:
    return await posts_service.get_posts(last_id, limit)


@router.post(
    path="/{post_id}/like",
    summary="Лайк поста",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Пост успешно лайкнут"},
        409: {
            "description": "Пост уже лайкнут",
            "content": {"application/json": {"schema": {"detail": "Already liked"}}},
        },
        404: {
            "description": "Пост не найден",
            "content": {
                "application/json": {"schema": ExceptionSchema.model_json_schema()}
            },
        },
    },
    tags=["Posts"],
)
async def like_post(
    post_id: str,
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    posts_service: PostsService = Depends(get_posts_service),
) -> None:
    res = await posts_service.like_post(post_id, user_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already liked"
        )


@router.post(
    path="/{post_id}/dislike",
    summary="Дизлайк поста",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Пост успешно дизлайкнут"},
        409: {
            "description": "Пост уже дизлайкнут",
            "content": {"application/json": {"schema": {"detail": "Already disliked"}}},
        },
        404: {
            "description": "Пост не найден",
            "content": {
                "application/json": {"schema": ExceptionSchema.model_json_schema()}
            },
        },
    },
    tags=["Posts"],
)
async def dislike_post(
    post_id: str,
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    posts_service: PostsService = Depends(get_posts_service),
) -> None:
    res = await posts_service.dislike_post(post_id, user_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already disliked"
        )


# TODO: Комментарии workflow
