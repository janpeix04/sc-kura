import logging

from celery import states as task_states
from celery.result import AsyncResult
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.i18n import _

logger = logging.getLogger(__name__)


class CeleryTaskResponse(BaseModel):
    task_id: str
    state: str
    details: dict | None = None
    progress: int | None = None
    total: int | None = None


class PublicError(RuntimeError):
    """A possibly known error the message of which can be safely passed to
    inform the user. It can be raised inside a task and it will populate the
    {'error': <msg>} in the task response.
    """


class JsonCeleryTaskResponse(JSONResponse):
    """FastAPI response class that wraps Celery task status for REST API."""

    def __init__(
        self,
        task: AsyncResult,
        total: int | None = None,
        **kwargs,
    ):
        data = {}

        if "data" in kwargs:
            logger.warning(
                "data is provided by the task object, ignoring 'data' argument"
            )
            kwargs.pop("data")

        try:
            task_info = task.info if task.info is not None else {}
            task_state = task.state
        except ValueError:
            task_info = {}
            task_state = task_states.FAILURE
        progress = 0
        if isinstance(task_info, dict):
            progress = task_info.get("progress", 0)

        data.update(
            {
                "task_id": task.id,
                "state": task_state,
                "details": task_info,
                "progress": progress,
                "total": total,
            }
        )
        status_code = 200

        generic_public_error = _(
            "Something went wrong. Try re-loading the page if the issue persists."
        )
        if task_state == task_states.SUCCESS:
            data["details"] = task.get()
        elif task_state in [
            task_states.PENDING,
            task_states.STARTED,
            task_states.RECEIVED,
        ]:
            status_code = 202
        elif task_state in [task_states.FAILURE, task_states.REVOKED]:
            if isinstance(task.result, PublicError):
                data["details"] = {"error": str(task.result)}
            else:
                data["details"] = {"error": (generic_public_error)}
            task.forget()
        elif task_state == task_states.RETRY:
            status_code = 202

        kwargs["status_code"] = status_code
        try:
            super().__init__(content=data, **kwargs)
        except Exception as e:
            logger.error(f"Error creating CeleryTaskResponse: {e}")
            super().__init__(
                {
                    "task_id": task.id,
                    "state": task_states.FAILURE,
                    "details": {"error": generic_public_error},
                    "progress": 0,
                    "total": total,
                },
                **kwargs,
            )
