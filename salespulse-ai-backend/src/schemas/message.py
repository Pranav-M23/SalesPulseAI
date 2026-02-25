from pydantic import BaseModel
from typing import Optional

class MessageCreate(BaseModel):
    content: str
    channel_id: int
    campaign_id: Optional[int] = None
    contact_id: Optional[int] = None

class MessageResponse(BaseModel):
    id: int
    content: str
    channel_id: int
    campaign_id: Optional[int] = None
    contact_id: Optional[int] = None
    created_at: str

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    channel_id: Optional[int] = None
    campaign_id: Optional[int] = None
    contact_id: Optional[int] = None