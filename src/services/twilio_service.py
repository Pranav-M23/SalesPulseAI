import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from src.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import TwilioServiceError

_client = None


def _get_client():
    global _client
    if _client is None:
        account_sid = settings.TWILIO_ACCOUNT_SID or os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = settings.TWILIO_AUTH_TOKEN or os.getenv("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            raise TwilioServiceError("Twilio credentials not configured")

        logger.info(f"Initializing Twilio client with SID: {account_sid[:6]}...")
        _client = Client(account_sid, auth_token)
    return _client


async def send_whatsapp(to, message):
    logger.info(f"Sending WhatsApp to {to}")
    try:
        client = _get_client()
        whatsapp_from = settings.TWILIO_WHATSAPP_NUMBER or os.getenv("TWILIO_WHATSAPP_NUMBER")
        whatsapp_to = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
        msg = client.messages.create(
            from_=whatsapp_from,
            body=message,
            to=whatsapp_to,
        )
        logger.info(f"WhatsApp sent: sid={msg.sid} status={msg.status}")
        return {"message_id": msg.sid, "status": msg.status}
    except TwilioServiceError:
        raise
    except Exception as e:
        logger.error(f"Twilio WhatsApp error: {e}")
        raise TwilioServiceError(f"Failed to send WhatsApp: {str(e)}")


async def send_sms(to, message):
    logger.info(f"Sending SMS to {to}")
    try:
        client = _get_client()
        sms_from = settings.TWILIO_SMS_NUMBER or os.getenv("TWILIO_SMS_NUMBER")
        msg = client.messages.create(
            from_=sms_from,
            body=message,
            to=to,
        )
        logger.info(f"SMS sent: sid={msg.sid} status={msg.status}")
        return {"message_id": msg.sid, "status": msg.status}
    except TwilioServiceError:
        raise
    except Exception as e:
        logger.error(f"Twilio SMS error: {e}")
        raise TwilioServiceError(f"Failed to send SMS: {str(e)}")


def build_twiml_response(reply_text):
    response = MessagingResponse()
    response.message(reply_text)
    return str(response)
