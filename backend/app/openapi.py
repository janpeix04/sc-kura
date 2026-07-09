import re
from typing import Any

from pydantic import BaseModel
from pydantic.json_schema import model_json_schema

from http import HTTPStatus

from app.core.config import settings


def collect_specs_from_dependant(dependant) -> dict[int, dict[str, Any]]:
    merged: dict[int, dict[str, Any]] = {}
    seen: set[int] = set()

    def walk(d):
        if d is None:
            return

        oid = id(d)
        if oid in seen:
            return

        seen.add(oid)
        specs = getattr(getattr(d, "call", None), "_response_spec", None)

        if specs:
            for code, entry in specs.items():
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


def spec_to_openapi_response(
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


def build_operation_id(methods, path_format: str) -> str:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    method = list(methods)[0]
    route_path = path_format.removeprefix(settings.API_PREFIX)
    route_path = re.sub(r"\W", "_", route_path)
    return f"{route_path}_{method}"
