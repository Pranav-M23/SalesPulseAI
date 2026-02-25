from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.twilio_service import handle_twilio_webhook
from core.logging import logger

router = APIRouter()

class TwilioWebhookRequest(BaseModel):
    From: str
    To: str
    Body: str

@router.post("/webhooks/twilio")
async def twilio_webhook(request: Request, webhook_data: TwilioWebhookRequest):
    logger.info(f"Received webhook from Twilio: {webhook_data}")
    try:
        response = await handle_twilio_webhook(webhook_data)
        return {"status": "success", "data": response}
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")