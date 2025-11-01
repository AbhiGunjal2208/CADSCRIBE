"""
Tests for the main FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cadscribe-backend"
    assert "timestamp" in data


def test_detailed_health_check():
    """Test the detailed health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "services" in data
    assert "environment" in data


def test_docs_endpoint():
    """Test that the API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    """Test that the ReDoc documentation is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200
