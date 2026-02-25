from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_send_message_via_whatsapp():
    response = client.post("/v1/channels/whatsapp/send", json={"message": "Hello, World!", "to": "+1234567890"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Message sent via WhatsApp"}

def test_send_message_via_sms():
    response = client.post("/v1/channels/sms/send", json={"message": "Hello, World!", "to": "+1234567890"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Message sent via SMS"}

def test_send_message_via_email():
    response = client.post("/v1/channels/email/send", json={"subject": "Test", "body": "Hello, World!", "to": "test@example.com"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Email sent successfully"}