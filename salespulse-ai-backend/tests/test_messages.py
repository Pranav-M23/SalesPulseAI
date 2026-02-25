from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_generate_message():
    response = client.post("/v1/generate-message", json={"lead_data": {"name": "John Doe", "interest": "AI"}})
    assert response.status_code == 200
    assert "message" in response.json()

def test_send_message_via_whatsapp():
    response = client.post("/v1/channels/whatsapp/send", json={"message": "Hello, John!", "to": "+1234567890"})
    assert response.status_code == 200
    assert response.json()["status"] == "sent"

def test_send_message_via_sms():
    response = client.post("/v1/channels/sms/send", json={"message": "Hello, John!", "to": "+1234567890"})
    assert response.status_code == 200
    assert response.json()["status"] == "sent"

def test_send_message_via_email():
    response = client.post("/v1/channels/email/send", json={"message": "Hello, John!", "to": "john@example.com"})
    assert response.status_code == 200
    assert response.json()["status"] == "sent"