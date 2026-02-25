from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SalesStage(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"
    RE_ENGAGEMENT = "re_engagement"


class MessageTone(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    CONSULTATIVE = "consultative"
    CASUAL = "casual"


class GenerateMessageRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    industry: str = Field(..., min_length=1, max_length=100)
    pain_point: str = Field(..., min_length=1, max_length=500)
    stage: SalesStage = Field(...)
    tone: MessageTone = Field(default=MessageTone.FRIENDLY)
    use_ai_rewrite: bool = Field(default=True)


class GenerateMessageResponse(BaseModel):
    success: bool = True
    subject: str
    message: str
    cta: str
    score: float = Field(..., ge=0, le=100)
    stage: str
    tone: str


class SendWhatsAppRequest(BaseModel):
    to: str = Field(..., pattern=r"^\+\d{10,15}$")
    message: str = Field(..., min_length=1, max_length=4096)


class SendSMSRequest(BaseModel):
    to: str = Field(..., pattern=r"^\+\d{10,15}$")
    message: str = Field(..., min_length=1, max_length=1600)


class SendEmailRequest(BaseModel):
    to_email: str = Field(...)
    to_name: Optional[str] = Field(default=None, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=50000)
    html: Optional[bool] = Field(default=False)


class SendMessageResponse(BaseModel):
    success: bool = True
    channel: str
    recipient: str
    message_id: Optional[str] = None
    detail: str = "Message sent successfully"
