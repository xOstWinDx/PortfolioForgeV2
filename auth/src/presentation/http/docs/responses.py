from src.presentation.http.exc_schema import (
    AuthenticationErrorSchema,
    NotFoundErrorSchema,
    AuthorizationErrorSchema,
    ConflictErrorSchema,
    ErrorDetail,
)


class ResponsesEnum:
    R_401 = {
        "description": "Неверные учетные данные",
        "content": {
            "application/json": {
                "schema": AuthenticationErrorSchema.model_json_schema()
            },
        },
    }
    R_403 = {
        "description": "Недостаточно прав для изменения фотографии пользователя",
        "content": {
            "application/json": {"schema": AuthorizationErrorSchema.model_json_schema()}
        },
    }
    R_404 = {
        "description": "Сущность не найдена",
        "content": {
            "application/json": {"schema": NotFoundErrorSchema.model_json_schema()}
        },
    }
    R_409 = {
        "description": "Конфликт данных",
        "content": {
            "application/json": {"schema": ConflictErrorSchema.model_json_schema()}
        },
    }
    R_422 = {
        "description": "Ошибка валидации входных данных",
        "content": {"application/json": {"schema": ErrorDetail.model_json_schema()}},
    }
