from app.celery import app
from typing import Any
import time
import requests

@app.task
def io_bound_task(url):
    response = requests.get(url)
    return response.status_code

@app.task
def collect_results(results: Any, start_time: float):
    end_time = time.time()
    return { "status": results, "time_taken": end_time - start_time}
