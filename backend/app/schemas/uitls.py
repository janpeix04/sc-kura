from typing import Any

from pydantic import BaseModel


class HTTPMessage(BaseModel):
    msg: str  # message that can face the user
    loc: str | None = None  # if from a form, for example, what field it comes from
    meta: dict[str, Any] | None = None  # additional fields


class HTTPError(Exception):
    def __init__(
        self,
        status_code: int,
        msg: str,
        loc: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = HTTPMessage(msg=msg, loc=loc, meta=meta)


def add_responses(*codes: int, models: dict[int, BaseModel] | None = None):
    if models is None:
        return {code: {"model": HTTPMessage} for code in codes}
    return {code: {"model": model} for code, model in models.items()}


def error_codes(*codes: int, models: dict[int, BaseModel] | None = None):
    def decorator(func):
        func._response_spec = add_responses(*codes, models=models)
        return func

    return decorator


class HealthCheck(BaseModel):
    name: str
    version: str
    description: str
