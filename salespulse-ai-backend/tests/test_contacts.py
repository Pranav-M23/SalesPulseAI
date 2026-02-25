from fastapi.testclient import TestClient
from src.main import app
from src.models.contact import Contact
from src.schemas.contact import ContactCreate

client = TestClient(app)

def test_create_contact():
    contact_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/v1/contacts/", json=contact_data)
    assert response.status_code == 201
    assert response.json()["name"] == contact_data["name"]

def test_get_contact():
    response = client.get("/api/v1/contacts/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_update_contact():
    updated_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "0987654321"
    }
    response = client.put("/api/v1/contacts/1", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]

def test_delete_contact():
    response = client.delete("/api/v1/contacts/1")
    assert response.status_code == 204

def test_get_nonexistent_contact():
    response = client.get("/api/v1/contacts/999")
    assert response.status_code == 404