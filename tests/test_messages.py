import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_generate_message_without_ai(client):
    payload = {
        "name": "Alice Johnson",
        "role": "VP of Sales",
        "company": "Acme Corp",
        "industry": "SaaS",
        "pain_point": "low reply rates on cold outreach",
        "stage": "prospecting",
        "tone": "friendly",
        "use_ai_rewrite": False,
    }
    response = await client.post("/generate-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["message"]) > 20
    assert len(data["cta"]) > 5
    assert 0 <= data["score"] <= 100
    assert data["stage"] == "prospecting"
    assert data["tone"] == "friendly"


@pytest.mark.anyio
async def test_generate_message_with_ai_rewrite(client):
    mock_return = {
        "subject": "AI Improved Subject",
        "message": "AI improved body that is optimized for reply rates.",
        "cta": "Book a call now",
    }
    with patch(
        "src.api.v1.endpoints.messages.rewrite_message",
        new_callable=AsyncMock,
        return_value=mock_return,
    ):
        payload = {
            "name": "Bob Smith",
            "role": "CTO",
            "company": "TechInc",
            "industry": "Fintech",
            "pain_point": "slow onboarding process",
            "stage": "qualification",
            "tone": "consultative",
            "use_ai_rewrite": True,
        }
        response = await client.post("/generate-message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject"] == "AI Improved Subject"


@pytest.mark.anyio
async def test_generate_message_validation_error(client):
    payload = {"name": "Alice"}
    response = await client.post("/generate-message", json=payload)
    assert response.status_code == 422
