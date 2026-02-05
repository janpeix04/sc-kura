import re

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import router

from app.core.config import settings

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


@app.get("/healthcheck/")
def health_check():
    return {"status": "ok"}


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


use_route_names_as_operation_ids(app)
