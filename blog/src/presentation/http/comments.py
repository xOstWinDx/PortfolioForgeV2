from datetime import datetime, UTC

from bson import ObjectId
from fastapi import APIRouter, Header, Depends, HTTPException, Query
from starlette import status

from src.application.services.comments import CommentsService
from src.domain.comment import Comment
from src.infrastructure.schemas.comment import (
    CommentReadSchema,
    CommentCreateSchema,
    AnswersReposeSchema,
    CommentsReposeSchema,
)
from src.infrastructure.schemas.exceptions import ExceptionSchema, ValidationErrorSchema
from src.presentation.http.dependencies import oauth2_scheme, get_comments_service

router = APIRouter()


@router.get(
    path="/{post_id}/comments",
    status_code=status.HTTP_200_OK,
    summary="Получить комментарии к посту",
    response_model=CommentsReposeSchema,
    responses={
        200: {"description": "Успешное получение комментариев"},
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
async def get_comments(
    post_id: str,
    last_id: str | None,
    limit: int = Query(le=20, default=10, ge=1),
    comments_service: CommentsService = Depends(get_comments_service),
) -> CommentsReposeSchema:
    res = await comments_service.get(
        post_id=post_id, parent_id=None, last_id=last_id, limit=limit
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Can't get comments, post not found with id: {post_id}",
        )
    return res  # noqa


@router.get(
    path="/{post_id}/comments/{comment_id}/answers",
    status_code=status.HTTP_200_OK,
    summary="Получить ответы на комментарий",
    response_model=AnswersReposeSchema,
    responses={
        200: {"description": "Успешное получение ответов"},
        404: {
            "description": "Комментарий не найден",
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
)
async def get_answers(
    post_id: str,
    comment_id: str,
    last_id: str,
    limit: int = Query(10, le=20, ge=1),
    comments_service: CommentsService = Depends(get_comments_service),
) -> AnswersReposeSchema:
    res = await comments_service.get(
        post_id=post_id, parent_id=comment_id, last_id=last_id, limit=limit
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Can't get answers, comment not found with id: {comment_id}",
        )
    return res  # noqa


@router.post(
    path="/{post_id}/comments/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить комментарий",
    response_model=CommentReadSchema,
    responses={
        201: {"description": "Комментарий успешно добавлен"},
        401: {"description": "Пользователь не авторизован"},
        404: {"description": "Пост не найден"},
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
async def create_comment(
    post_id: str,
    comment: CommentCreateSchema,
    comments_service: CommentsService = Depends(get_comments_service),
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    _: str = Depends(oauth2_scheme),  # для документации
) -> CommentReadSchema:
    result = await comments_service.create(
        comment=Comment(
            id=str(ObjectId()),
            text=comment.text,
            author=None,
            post_id=post_id,
            parent_id=None,
            created_at=datetime.now(UTC),
            answers_count=0,
            likes=0,
            dislikes=0,
        ),
        user_id=user_id,
    )
    return result  # noqa


@router.post(
    path="/{post_id}/comments/{comment_id}/answer",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ответ на комментарий",
    response_model=CommentReadSchema,
    responses={
        201: {"description": "Ответ успешно добавлен"},
        401: {"description": "Пользователь не авторизован"},
        404: {
            "description": "Комментарий не найден",
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
)
async def create_answer(
    post_id: str,
    comment_id: str,
    comment: CommentCreateSchema,
    comments_service: CommentsService = Depends(get_comments_service),
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    _: str = Depends(oauth2_scheme),  # для документации
) -> CommentReadSchema:
    result = await comments_service.create(
        comment=Comment(
            id=str(ObjectId()),
            text=comment.text,
            author=None,
            post_id=post_id,
            parent_id=comment_id,
            created_at=datetime.now(UTC),
            answers_count=0,
            likes=0,
            dislikes=0,
        ),
        user_id=user_id,
    )
    return result  # noqa


@router.post(
    path="/{post_id}/comments/{comment_id}/like",
    summary="Лайк комментария",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Комментарий успешно лайкнут"},
        401: {
            "description": "Пользователь не авторизован",
        },
        409: {
            "description": "Комментарий уже лайкнут",
            "content": {"application/json": {"schema": {"detail": "Already liked"}}},
        },
        404: {
            "description": "Комментарий не найден",
            "content": {
                "application/json": {"schema": ExceptionSchema.model_json_schema()}
            },
        },
    },
    tags=["Posts"],
)
async def like_comment(
    post_id: str,  # noqa
    comment_id: str,
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    comments_service: CommentsService = Depends(get_comments_service),
    _: str = Depends(oauth2_scheme),  # для документации.
) -> None:
    res = await comments_service.like(comment_id, user_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already liked"
        )


@router.post(
    path="/{post_id}/comments/{comment_id}/dislike",
    summary="Дизайк комментария",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Комментарий успешно дизайкнут"},
        401: {
            "description": "Пользователь не авторизован",
        },
        409: {
            "description": "Комментарий уже дизайкнут",
            "content": {"application/json": {"schema": {"detail": "Already disliked"}}},
        },
        404: {
            "description": "Комментарий не найден",
            "content": {
                "application/json": {"schema": ExceptionSchema.model_json_schema()}
            },
        },
    },
    tags=["Posts"],
)
async def dislike_comment(
    post_id: str,  # noqa
    comment_id: str,
    user_id: int = Header(alias="X-User-ID", include_in_schema=False),
    comments_service: CommentsService = Depends(get_comments_service),
    _: str = Depends(oauth2_scheme),  # для документации.
) -> None:
    res = await comments_service.dislike(comment_id, user_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already disliked"
        )
