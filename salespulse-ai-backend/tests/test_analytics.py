from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    assert "data" in response.json()

def test_post_analytics():
    response = client.post("/analytics", json={"metric": "message_sent", "value": 1})
    assert response.status_code == 201
    assert response.json() == {"message": "Analytics data recorded successfully."}