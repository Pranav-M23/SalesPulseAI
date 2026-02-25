import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_send_whatsapp(client):
    mock_result = {"message_id": "SM123", "status": "queued"}
    with patch(
        "src.api.v1.endpoints.channels.send_whatsapp",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        payload = {"to": "+14155551234", "message": "Hello from SalesPulse AI!"}
        response = await client.post("/send/whatsapp", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["channel"] == "whatsapp"


@pytest.mark.anyio
async def test_send_sms(client):
    mock_result = {"message_id": "SM456", "status": "queued"}
    with patch(
        "src.api.v1.endpoints.channels.send_sms",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        payload = {"to": "+14155551234", "message": "SMS from SalesPulse AI"}
        response = await client.post("/send/sms", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["channel"] == "sms"


@pytest.mark.anyio
async def test_send_email(client):
    mock_result = {"message_id": "msg-789", "status_code": 202}
    with patch(
        "src.api.v1.endpoints.channels.send_email",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        payload = {
            "to_email": "lead@example.com",
            "to_name": "Jane Doe",
            "subject": "Follow-up from SalesPulse AI",
            "body": "Hi Jane, just checking in...",
            "html": False,
        }
        response = await client.post("/send/email", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["channel"] == "email"


@pytest.mark.anyio
async def test_send_whatsapp_invalid_phone(client):
    payload = {"to": "not-a-phone", "message": "Hello"}
    response = await client.post("/send/whatsapp", json=payload)
    assert response.status_code == 422
