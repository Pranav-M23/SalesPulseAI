import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_whatsapp_webhook(client):
    with patch(
        "src.api.v1.endpoints.webhooks.chat_completion",
        new_callable=AsyncMock,
        return_value="Thanks for reaching out! How can I help?",
    ), patch(
        "src.api.v1.endpoints.webhooks.store_message",
        new_callable=AsyncMock,
    ), patch(
        "src.api.v1.endpoints.webhooks.get_recent_messages",
        new_callable=AsyncMock,
        return_value=[{"role": "user", "content": "Hi there"}],
    ):
        response = await client.post(
            "/webhook/whatsapp",
            data={"Body": "Hi there", "From": "whatsapp:+14155551234"},
        )
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
        assert "<Response>" in response.text
        assert "<Message>" in response.text


@pytest.mark.anyio
async def test_sms_webhook(client):
    with patch(
        "src.api.v1.endpoints.webhooks.chat_completion",
        new_callable=AsyncMock,
        return_value="Great to hear from you!",
    ), patch(
        "src.api.v1.endpoints.webhooks.store_message",
        new_callable=AsyncMock,
    ), patch(
        "src.api.v1.endpoints.webhooks.get_recent_messages",
        new_callable=AsyncMock,
        return_value=[{"role": "user", "content": "Hello"}],
    ):
        response = await client.post(
            "/webhook/sms",
            data={"Body": "Hello", "From": "+14155551234"},
        )
        assert response.status_code == 200
        assert "<Response>" in response.text
