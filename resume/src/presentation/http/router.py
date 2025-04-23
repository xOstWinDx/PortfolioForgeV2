from fastapi import Depends, Query, HTTPException, APIRouter

from src.application.interfaces.uow import AbstractUnitOfWork
from src.application.services.profile import ProfileService
from src.application.services.project import ProjectService
from src.domain.filters.projects import ProjectsFilter
from src.infrastructure.models import ProjectRead, ProfileRead
from src.presentation.http.dependencies import (
    get_uow,
    get_profile_service,
    get_project_service,
)
from src.presentation.http.docs.responses import R_422

router = APIRouter()


@router.get(
    "/profile",
    status_code=200,
    summary="Визитка",
    description="Возвращает данные для главной страницы",
    responses={200: {"description": "Успешное получение визитки"}},
    response_model=ProfileRead,
    tags=["Profile"],
)
async def get_profile(
    profile_service: ProfileService = Depends(get_profile_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ProfileRead:
    async with uow:
        profile = await profile_service.get_profile(uow)
        return ProfileRead.model_validate(profile, from_attributes=True)


@router.get(
    "/projects",
    summary="Список проектов",
    status_code=200,
    response_model=list[ProjectRead],
    responses={200: {"description": "Успешное получение списка проектов"}, 422: R_422},
    tags=["Projects"],
)
async def get_projects(
    featured: bool = Query(None, description="Показать только избранные"),
    project_service: ProjectService = Depends(get_project_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    offset: int = Query(ge=0, default=0, description="Смещение по страницам"),
    limit: int = Query(
        gt=0, default=10, description="Количество элементов на странице"
    ),
) -> list[ProjectRead]:
    async with uow:
        return await project_service.get(  # type: ignore # noqa
            ProjectsFilter(is_featured=featured), uow, limit=limit, offset=offset
        )


@router.get(
    "/projects/{project_id}",
    response_model=ProjectRead,
    summary="Получить проект",
    status_code=200,
    responses={
        200: {"description": "Успешное получение проекта"},
        404: {
            "description": "Проект не найден",
            "content": {
                "application/json": {"schema": {"detail": "Project not found"}}
            },
        },
        422: R_422,
    },
    tags=["Projects"],
)
async def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ProjectRead:
    async with uow:
        projects = await project_service.get(
            ProjectsFilter(id=project_id), uow, limit=1, offset=0
        )
        if not projects:
            raise HTTPException(status_code=404, detail="Project not found")
        return projects[0]  # noqa


@router.get("/health", status_code=200, include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
