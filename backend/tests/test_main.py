import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI with DocumentDB!"}


def test_docs_endpoint():
    """Test that the API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "FastAPI" in response.text


def test_openapi_endpoint():
    """Test the OpenAPI schema endpoint"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "Full Stack FastAPI DocumentDB"