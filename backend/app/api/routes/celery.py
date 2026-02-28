from fastapi import APIRouter
from app.tasks import collect_results

router = APIRouter(prefix="/celery", tags=["celery"])


@router.get("/result/{task_id}/")
def get_result(task_id: str):
    task = collect_results.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "Task is still in progress", "state": task.state}
    elif task.state != "FAILURE":
        return task.result
    else:
        return {"status": "Task failed", "state": task.state, "error": str(task.info)}
