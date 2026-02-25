from fastapi import APIRouter, Request
from fastapi.responses import Response, JSONResponse
from src.services.trigger_service import handle_lead_reply
from src.services.twilio_service import build_twiml_response
from src.config.settings import settings
from src.core.logging import logger

router = APIRouter()


# ─── Twilio WhatsApp Webhook ───────────────────────────────────────────────────

from fastapi import Body

# --- WhatsApp Webhook ---
@router.post("/whatsapp", summary="WhatsApp webhook for incoming messages", tags=["Webhooks"], response_description="AI-generated reply sent to user")
async def whatsapp_webhook(
    request: Request,
    Body: str = Body(None, description="Incoming message body (Twilio: form, Meta: JSON)", embed=True),
    From: str = Body(None, description="Sender phone number (Twilio: form, Meta: JSON)", embed=True),
    messages: dict = Body(None, description="Meta WhatsApp: messages payload", embed=True),
    type: str = Body(None, description="Meta WhatsApp: message type", embed=True),
    chat_id: str = Body(None, description="Meta WhatsApp: chat id", embed=True),
    id: str = Body(None, description="Meta WhatsApp: message id", embed=True),
):
    """
    Webhook endpoint for WhatsApp (Twilio or Meta/Whapi).
    - Twilio: expects form fields 'Body' and 'From'.
    - Meta/Whapi: expects JSON with 'messages', 'type', 'chat_id', 'id'.
    On receiving a user reply, generates a Groq AI response and sends it back.
    """
    provider = settings.WHATSAPP_PROVIDER
    if provider == "meta":
        return await _handle_meta_whatsapp_post(request)
    else:
        return await _handle_twilio_whatsapp_post(request)


async def _handle_twilio_whatsapp_post(request: Request):
    """Handle Twilio-format WhatsApp webhook."""
    try:
        form_data = await request.form()
        body = str(form_data.get("Body", "")).strip()
        from_number = str(form_data.get("From", "")).strip()

        logger.info(f"Twilio WhatsApp webhook: From={from_number} Body={body[:80]}")

        if not body:
            twiml = build_twiml_response("I didn't receive a message. Could you try again?")
            return Response(content=twiml, media_type="application/xml")

        if not from_number:
            twiml = build_twiml_response("Sorry, something went wrong.")
            return Response(content=twiml, media_type="application/xml")

        ai_reply = await handle_lead_reply(
            phone_number=from_number,
            message_text=body,
            channel="whatsapp",
        )

        twiml = build_twiml_response(ai_reply)
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Twilio WhatsApp webhook error: {e}")
        twiml = build_twiml_response("Sorry, I encountered an error. Please try again.")
        return Response(content=twiml, media_type="application/xml")


# ─── Meta WhatsApp Cloud API Webhook ──────────────────────────────────────────

async def _handle_meta_whatsapp_post(request: Request):
    """Handle Whapi webhook (incoming WhatsApp messages)."""
    try:
        data = await request.json()
        logger.info(f"Whapi webhook received: {str(data)[:200]}")

        # Whapi sends messages as a list or single object
        messages = data.get("messages", [])
        if not isinstance(messages, list):
            messages = [messages]

        for msg in messages:
            if not msg:
                continue

            # Skip outgoing messages (from_me = True means we sent it)
            if msg.get("from_me", False):
                continue

            msg_type = msg.get("type", "text")
            chat_id = msg.get("chat_id", "")  # e.g. "919876543210@s.whatsapp.net"
            from_number = msg.get("from", chat_id.split("@")[0] if "@" in chat_id else "")
            msg_id = msg.get("id", "")

            if msg_type == "text":
                body = msg.get("text", {}).get("body", "").strip()
            else:
                body = f"[{msg_type} message received]"
                logger.info(f"Non-text message type: {msg_type}")

            if not body or not from_number:
                continue

            # Clean up the from_number
            clean_from = from_number.replace("@s.whatsapp.net", "")
            logger.info(f"Whapi WhatsApp: From=+{clean_from} Body={body[:80]}")

            # Mark as read
            from src.services.meta_whatsapp_service import mark_message_read
            await mark_message_read(msg_id)

            # Generate AI reply
            ai_reply = await handle_lead_reply(
                phone_number=f"+{clean_from}",
                message_text=body,
                channel="whatsapp",
            )

            # Send reply via Whapi
            from src.services.meta_whatsapp_service import send_whatsapp
            await send_whatsapp(to=f"+{clean_from}", message=ai_reply)

        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        logger.error(f"Whapi webhook error: {e}")
        return JSONResponse(content={"status": "error"}, status_code=200)


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """Handles webhook verification / health check."""
    provider = settings.WHATSAPP_PROVIDER
    return {
        "status": "WhatsApp webhook is active",
        "provider": provider,
        "method": "POST required",
    }


# ─── Twilio SMS Webhook ───────────────────────────────────────────────────────

@router.post("/sms")
async def sms_webhook(request: Request):
    """Handle incoming SMS messages — auto-replies with Groq AI."""
    try:
        form_data = await request.form()
        body = str(form_data.get("Body", "")).strip()
        from_number = str(form_data.get("From", "")).strip()

        logger.info(f"SMS webhook: From={from_number} Body={body[:80]}")

        if not body:
            twiml = build_twiml_response("I didn't receive a message. Could you try again?")
            return Response(content=twiml, media_type="application/xml")

        if not from_number:
            twiml = build_twiml_response("Sorry, something went wrong.")
            return Response(content=twiml, media_type="application/xml")

        ai_reply = await handle_lead_reply(
            phone_number=from_number,
            message_text=body,
            channel="sms",
        )

        twiml = build_twiml_response(ai_reply)
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"SMS webhook error: {e}")
        twiml = build_twiml_response("Sorry, I encountered an error. Please try again.")
        return Response(content=twiml, media_type="application/xml")


@router.get("/sms")
async def sms_webhook_test():
    return {"status": "SMS webhook is active", "method": "POST required"}
