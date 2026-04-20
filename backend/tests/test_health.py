from fastapi.testclient import TestClient
from app.core.config import settings

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {
        "title": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
    }
