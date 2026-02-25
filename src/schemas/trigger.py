from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class TriggerType(str, Enum):
    SCHEDULED = "scheduled"          # Send at a specific time
    FOLLOW_UP = "follow_up"          # Auto follow-up after X hours
    NO_RESPONSE = "no_response"      # Trigger when no reply received
    RE_ENGAGEMENT = "re_engagement"  # Re-engage cold leads
    DRIP = "drip"                    # Drip campaign sequence


class TriggerChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"


class TriggerStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateTriggerRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    trigger_type: TriggerType
    channel: TriggerChannel
    recipient: str = Field(..., min_length=1)
    recipient_name: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=5000)
    subject: Optional[str] = None  # For email
    delay_minutes: int = Field(default=60, ge=0, le=43200)  # 0 min to 30 days
    max_retries: int = Field(default=3, ge=1, le=10)
    stop_on_reply: bool = Field(default=True)


class TriggerResponse(BaseModel):
    success: bool = True
    trigger_id: int
    name: str
    trigger_type: str
    channel: str
    recipient: str
    status: str
    delay_minutes: int
    scheduled_at: Optional[str] = None
    detail: str = "Trigger created successfully"


class TriggerListResponse(BaseModel):
    success: bool = True
    total: int
    triggers: List[dict]


class CreateDripCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    channel: TriggerChannel
    recipient: str = Field(..., min_length=1)
    recipient_name: Optional[str] = None
    subject_prefix: Optional[str] = None
    messages: List[str] = Field(..., min_length=1, max_length=10)
    delay_between_minutes: int = Field(default=1440, ge=0)  # Default 24 hours
    stop_on_reply: bool = Field(default=True)


class DripCampaignResponse(BaseModel):
    success: bool = True
    campaign_name: str
    total_steps: int
    trigger_ids: List[int]
    detail: str = "Drip campaign created successfully"