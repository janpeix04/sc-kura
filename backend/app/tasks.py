import asyncio
import time

from typing import Any

from app.celery import app
from app.emails import (
    send_email,
    generate_new_account_email,
    generate_reset_password_email,
)


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


@app.task
def send_reset_password_email(username: str, email: str, reset_password_link: str):
    email_data = generate_reset_password_email(
        username=username, reset_password_link=reset_password_link
    )
    asyncio.run(send_email(email_data=email_data, email_to=email))
    return f"Email sent to {email}"
