from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.services.twilio_service import send_whatsapp_message, send_sms_message
from src.services.email_service import send_email

router = APIRouter()

class MessageRequest(BaseModel):
    to: str
    message: str

@router.post("/send-whatsapp", response_model=dict)
async def send_whatsapp(request: MessageRequest):
    try:
        response = await send_whatsapp_message(request.to, request.message)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-sms", response_model=dict)
async def send_sms(request: MessageRequest):
    try:
        response = await send_sms_message(request.to, request.message)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@router.post("/send-email", response_model=dict)
async def send_email_endpoint(request: EmailRequest):
    try:
        response = await send_email(request.to, request.subject, request.body)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))