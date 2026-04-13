from celery.result import AsyncResult
from fastapi import APIRouter

from app.celery import app
from app.schemas.tasks import CeleryTaskResponse, JsonCeleryTaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}/", response_model=CeleryTaskResponse)
async def get_task_status(task_id: str) -> JsonCeleryTaskResponse:
    """Get the status of a Celery task by its ID."""
    task = AsyncResult(task_id, app=app)
    return JsonCeleryTaskResponse(task=task)
