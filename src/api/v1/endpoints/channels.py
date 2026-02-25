from fastapi import APIRouter
from src.schemas.message import (
    SendWhatsAppRequest,
    SendSMSRequest,
    SendEmailRequest,
    SendMessageResponse,
)
from src.config.settings import settings
from src.services.twilio_service import send_sms
from src.services.email_service import send_email
from src.services.conversation_service import store_sent_message
from src.core.logging import logger


def _get_whatsapp_sender():
    """Return the appropriate WhatsApp send function based on config."""
    if settings.WHATSAPP_PROVIDER == "meta":
        from src.services.meta_whatsapp_service import send_whatsapp
        return send_whatsapp
    else:
        from src.services.twilio_service import send_whatsapp
        return send_whatsapp

router = APIRouter()


@router.post("/whatsapp", response_model=SendMessageResponse)
async def send_whatsapp_endpoint(request: SendWhatsAppRequest):
    logger.info(f"POST /send/whatsapp to={request.to} (provider={settings.WHATSAPP_PROVIDER})")
    send_whatsapp = _get_whatsapp_sender()
    result = await send_whatsapp(to=request.to, message=request.message)
    await store_sent_message(
        recipient=request.to,
        channel="whatsapp",
        body=request.message,
        external_id=result.get("message_id"),
    )
    return SendMessageResponse(
        success=True,
        channel="whatsapp",
        recipient=request.to,
        message_id=result.get("message_id"),
        detail=f"WhatsApp sent (status={result.get('status')})",
    )


@router.post("/sms", response_model=SendMessageResponse)
async def send_sms_endpoint(request: SendSMSRequest):
    logger.info(f"POST /send/sms to={request.to}")
    result = await send_sms(to=request.to, message=request.message)
    await store_sent_message(
        recipient=request.to,
        channel="sms",
        body=request.message,
        external_id=result.get("message_id"),
    )
    return SendMessageResponse(
        success=True,
        channel="sms",
        recipient=request.to,
        message_id=result.get("message_id"),
        detail=f"SMS sent (status={result.get('status')})",
    )


@router.post("/email", response_model=SendMessageResponse)
async def send_email_endpoint(request: SendEmailRequest):
    logger.info(f"POST /send/email to={request.to_email}")
    result = await send_email(
        to_email=request.to_email,
        subject=request.subject,
        body=request.body,
        to_name=request.to_name,
        html=request.html or False,
    )
    await store_sent_message(
        recipient=request.to_email,
        channel="email",
        body=request.body,
        subject=request.subject,
        external_id=result.get("message_id"),
    )
    return SendMessageResponse(
        success=True,
        channel="email",
        recipient=request.to_email,
        message_id=result.get("message_id"),
        detail=f"Email sent (status_code={result.get('status_code')})",
    )
