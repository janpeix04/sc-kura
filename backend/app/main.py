import re
from typing import Any
from pydantic import BaseModel
from pydantic.json_schema import model_json_schema
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import router

from app.core.config import settings
from app.schemas.uitls import HealthCheck

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)
app.include_router(router, prefix=settings.API_V1_PREFIX)

origins = [
    f"http://localhost:{settings.FRONTEND_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
    }


def use_route_names_as_operation_ids(app: FastAPI):
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            assert route.methods
            if not route.path.endswith("/"):
                raise ValueError(f"Route '{route.path}' must end with '/'")
            method = list(route.methods)[0]
            route_path = route.path_format.removeprefix(settings.API_V1_PREFIX)
            route_path = re.sub(r"\W", "_", route_path)
            route.operation_id = f"{route_path}_{method}"


def _collect_specs_from_dependant(dependant) -> dict[int, dict[str, Any]]:
    merged: dict[int, dict[str, Any]] = {}
    seen: set[int] = set()

    def walk(d):
        if d is None:
            return
        oid = id(d)
        if oid in seen:
            return
        seen.add(oid)

        spec = getattr(getattr(d, "call", None), "_response_spec", None)
        if spec:
            for code, entry in spec.items():
                merged[code] = entry

        for sd in getattr(d, "dependencies", []):
            walk(sd)

    walk(dependant)
    return merged


def _ensure_components_schemas(schema: dict[str, Any]) -> dict[str, Any]:
    return schema.setdefault("components", {}).setdefault("schemas", {})


def _register_model_in_components(
    openapi_schema: dict[str, Any],
    model: type[BaseModel],
) -> str:
    components_schemas = _ensure_components_schemas(openapi_schema)
    name = model.__name__

    if name in components_schemas:
        return name

    json_schema = model_json_schema(
        model,
        ref_template="#/components/schemas/{model}",
    )

    defs = json_schema.pop("$defs", {})
    for def_name, def_schema in defs.items():
        components_schemas.setdefault(def_name, def_schema)

    components_schemas[name] = json_schema
    return name


def _spec_to_openapi_response(
    openapi_schema: dict[str, Any],
    code: int,
    spec: dict[str, Any],
) -> dict[str, Any]:
    model = spec.get("model")
    description = spec.get("description", HTTPStatus(code).phrase)

    entry = {"description": description}

    if model is None:
        return entry

    schema_name = _register_model_in_components(openapi_schema, model)
    entry["content"] = {
        "application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}
    }
    return entry


def install_openapi_response_merger(app: FastAPI):
    original_openapi = app.openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = original_openapi()

        for route in app.routes:
            dependant = getattr(route, "dependant", None)
            methods = getattr(route, "methods", None)
            if not dependant or not methods:
                continue

            dep_specs = _collect_specs_from_dependant(dependant)
            if not dep_specs:
                continue

            path_item = schema["paths"].get(route.path)
            if not path_item:
                continue

            dep_resps = {
                code: _spec_to_openapi_response(schema, code, spec)
                for code, spec in dep_specs.items()
            }

            for method in methods:
                op = path_item.get(method.lower())
                if not op:
                    continue
                existing = op.setdefault("responses", {})
                dep_resps = {str(key): res for key, res in dep_resps.items()}
                op["responses"] = {**dep_resps, **existing}

        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi


use_route_names_as_operation_ids(app)
install_openapi_response_merger(app)
