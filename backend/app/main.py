import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, iter_route_contexts

from sqlmodel.ext.asyncio.session import AsyncSession

from app import openapi
from app.core.config import settings
from app.schemas.utils import HealthCheck, HTTPError
from app.api.main import router
from app.i18n.runtime import activate, deactivate
from app.core.database import async_engine, init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSession(async_engine) as session:
        await init_db(session=session)
    yield


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)


def parse_locale(request: Request) -> str:
    x_locale = request.headers.get("x-locale")
    if x_locale:
        return x_locale.strip()

    accept = request.headers.get("accept-language")
    if not accept:
        return "en"

    first = accept.split(",")[0].strip()
    if first == "*" or first == "":
        return "en"

    return first


@app.middleware("http")
async def locale_middleware(request: Request, call_next):
    locale = parse_locale(request)
    logger.debug("LOCALE %s", locale)
    request.state.locale = locale
    token = activate(locale)
    try:
        return await call_next(request)
    finally:
        deactivate(token)


app.include_router(router, prefix=settings.API_PREFIX)


@app.exception_handler(HTTPError)
async def http_error_expection_handler(request: Request, exception: HTTPError):
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.message.model_dump(exclude_none=True),
    )


@app.get("/healthcheck/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "title": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
    }


def enforce_trailing_slash(app: FastAPI) -> None:
    for ctx in iter_route_contexts(app.routes):
        route = ctx.route

        if isinstance(route, APIRoute):
            if not route.path.endswith("/"):
                raise ValueError(f"Route '{route.path}' must end with '/'")


enforce_trailing_slash(app)


def install_openapi_response_merger(app: FastAPI):
    original_openapi = app.openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = original_openapi()

        for ctx in iter_route_contexts(app.routes):
            route = ctx.route

            if not isinstance(route, APIRoute):
                continue

            methods = getattr(route, "methods", None)
            if not methods:
                continue

            path_item = schema["paths"].get(ctx.path)
            if not path_item:
                continue

            first_method = next(iter(methods))
            op = path_item.get(first_method.lower())
            if op:
                op["operationId"] = openapi.build_operation_id(methods, ctx.path_format)

            dependant = getattr(route, "dependant", None)
            if not dependant:
                continue

            dep_specs = openapi.collect_specs_from_dependant(dependant)
            if not dep_specs:
                continue

            dep_resps = {
                str(code): openapi.spec_to_openapi_response(schema, code, spec)
                for code, spec in dep_specs.items()
            }

            for method in methods:
                op = path_item.get(method.lower())
                if not op:
                    continue
                existing = op.setdefault("responses", {})
                op["responses"] = {**dep_resps, **existing}

        return schema

    app.openapi = custom_openapi


install_openapi_response_merger(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Backend can only communicate with svk frontend running in the same machine.
        f"http://localhost:{settings.FRONTEND_PORT}"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
