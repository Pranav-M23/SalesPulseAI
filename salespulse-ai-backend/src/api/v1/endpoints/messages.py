from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.services.openai_service import generate_message
from src.services.template_engine import TemplateEngine

router = APIRouter()

class LeadData(BaseModel):
    name: str
    email: str
    phone: str
    interests: List[str]

class GeneratedMessage(BaseModel):
    message: str

@router.post("/generate-message", response_model=GeneratedMessage)
async def create_message(lead_data: LeadData):
    try:
        template_engine = TemplateEngine()
        message_template = template_engine.get_template(lead_data.interests)
        generated_message = await generate_message(lead_data, message_template)
        return GeneratedMessage(message=generated_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))