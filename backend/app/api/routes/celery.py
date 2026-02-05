import time

from fastapi import APIRouter

from app.tasks import io_bound_task, collect_results
from celery import chord

router = APIRouter(prefix="/celery", tags=["celery"])


@router.get("/sequential/")
def sequential_task():
    start_time = time.time()
    urls = ["https://httpbin.org/delay/3" for _ in range(10)]
    results = []
    for url in urls:
        results.append(io_bound_task(url))
    end_time = time.time()
    return {"status": results, "time_taken": end_time - start_time}


@router.get("/sequential/celery/")
def sequential_task_celery():
    start_time = time.time()
    urls = ["https://httpbin.org/delay/3" for _ in range(10)]
    tasks = [io_bound_task.s(url) for url in urls]
    callback = chord(tasks)(collect_results.s(start_time))
    return {"task_id": callback.id}


@router.get("/result/{task_id}/")
def get_result(task_id: str):
    task = collect_results.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "Task is still in progress", "state": task.state}
    elif task.state != "FAILURE":
        return task.result
    else:
        return {"status": "Task failed", "state": task.state, "error": str(task.info)}
