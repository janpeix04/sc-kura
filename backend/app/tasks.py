import asyncio
import time
import requests

from typing import Any

from app.celery import app
from app.emails import generate_new_account_email, send_email


@app.task
def io_bound_task(url):
    response = requests.get(url)
    return response.status_code


@app.task
def collect_results(results: Any, start_time: float):
    end_time = time.time()
    return {"status": results, "time_taken": end_time - start_time}


@app.task
def send_verification_email(username: str, email: str, verification_link: str):
    email_data = generate_new_account_email(
        username=username, email_to=email, verification_link=verification_link
    )
    asyncio.run(send_email(email_data=email_data, email_to=email))
    return f"Email sent to {email}"
