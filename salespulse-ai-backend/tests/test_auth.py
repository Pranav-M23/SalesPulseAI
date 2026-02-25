from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_authentication_success():
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_authentication_failure():
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 401
    assert "detail" in response.json()

def test_token_refresh():
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    access_token = response.json()["access_token"]
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert "access_token" in response.json()