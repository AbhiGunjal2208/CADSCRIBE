"""
Tests for authentication routes.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_signup():
    """Test user signup."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword"
    }
    
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user_data["email"]


def test_signup_duplicate_email():
    """Test signup with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "name": "Test User",
        "password": "testpassword"
    }
    
    # First signup should succeed
    response1 = client.post("/auth/signup", json=user_data)
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post("/auth/signup", json=user_data)
    assert response2.status_code == 400


def test_login():
    """Test user login."""
    # First create a user
    user_data = {
        "email": "login@example.com",
        "name": "Login User",
        "password": "loginpassword"
    }
    client.post("/auth/signup", json=user_data)
    
    # Then login
    login_data = {
        "email": "login@example.com",
        "password": "loginpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == login_data["email"]


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user information."""
    # First create a user and get token
    user_data = {
        "email": "current@example.com",
        "name": "Current User",
        "password": "currentpassword"
    }
    signup_response = client.post("/auth/signup", json=user_data)
    token = signup_response.json()["access_token"]
    
    # Use token to get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
