from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional
from src.services.conversation_service import (
    get_all_contacts,
    get_conversation_history,
    store_message,
    store_sent_message,
)
from src.config.settings import settings
from src.core.logging import logger

router = APIRouter()


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    channel: str = Field(default="whatsapp")


# ─── Contacts ──────────────────────────────────────────────────────────────────

@router.get("/contacts", tags=["Conversations"])
async def list_contacts(limit: int = Query(100, ge=1, le=500)):
    """List all known contacts derived from conversation history."""
    contacts = await get_all_contacts(limit=limit)
    return {"success": True, "total": len(contacts), "contacts": contacts}


# ─── Conversation History ───────────────────────────────────────────────────────

@router.get("/conversations/{phone_number}", tags=["Conversations"])
async def get_conversation(
    phone_number: str,
    limit: int = Query(100, ge=1, le=500),
):
    """Get the full conversation history for a contact."""
    history = await get_conversation_history(phone_number=phone_number, limit=limit)
    return {
        "success": True,
        "phone_number": phone_number,
        "total": len(history),
        "messages": history,
    }


# ─── Outbound Send ──────────────────────────────────────────────────────────────

@router.post("/conversations/{phone_number}/send", tags=["Conversations"])
async def send_to_contact(phone_number: str, request: SendMessageRequest):
    """Send an outbound message to a contact from the dashboard."""
    channel = request.channel.lower()

    if channel == "whatsapp":
        if settings.WHATSAPP_PROVIDER == "meta":
            from src.services.meta_whatsapp_service import send_whatsapp
        else:
            from src.services.twilio_service import send_whatsapp
        result = await send_whatsapp(to=phone_number, message=request.message)
        external_id = result.get("message_id")

    elif channel == "sms":
        from src.services.twilio_service import send_sms
        result = await send_sms(to=phone_number, message=request.message)
        external_id = result.get("message_id")

    elif channel == "email":
        return {"success": False, "detail": "Use POST /send/email for email messages."}

    else:
        return {"success": False, "detail": f"Unsupported channel: {channel}"}

    # Store in conversations so it appears in the chat window
    await store_message(
        phone_number=phone_number,
        role="assistant",
        message=request.message,
        channel=channel,
    )
    await store_sent_message(
        recipient=phone_number,
        channel=channel,
        body=request.message,
        external_id=external_id,
        status="manual_send",
    )

    logger.info(f"Dashboard outbound send to {phone_number} via {channel}: id={external_id}")
    return {
        "success": True,
        "phone_number": phone_number,
        "channel": channel,
        "message_id": external_id,
        "detail": "Message sent",
    }