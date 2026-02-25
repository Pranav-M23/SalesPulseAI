from fastapi.testclient import TestClient
from src.main import app
from src.models.campaign import Campaign
from src.schemas.campaign import CampaignCreate

client = TestClient(app)

def test_create_campaign():
    campaign_data = {
        "name": "Test Campaign",
        "description": "This is a test campaign.",
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "status": "active"
    }
    response = client.post("/api/v1/campaigns/", json=campaign_data)
    assert response.status_code == 201
    assert response.json()["name"] == campaign_data["name"]

def test_get_campaign():
    response = client.get("/api/v1/campaigns/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_update_campaign():
    updated_data = {
        "name": "Updated Campaign",
        "description": "This is an updated test campaign.",
        "start_date": "2023-01-01",
        "end_date": "2023-02-28",
        "status": "active"
    }
    response = client.put("/api/v1/campaigns/1", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]

def test_delete_campaign():
    response = client.delete("/api/v1/campaigns/1")
    assert response.status_code == 204
    response = client.get("/api/v1/campaigns/1")
    assert response.status_code == 404