from fastapi.testclient import TestClient
from app.core.config import settings

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
    }
