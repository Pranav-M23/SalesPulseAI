from pydantic import BaseModel
from typing import Optional

class ChannelBase(BaseModel):
    name: str
    type: str  # e.g., 'email', 'sms', 'whatsapp'
    active: bool

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(ChannelBase):
    name: Optional[str] = None
    type: Optional[str] = None
    active: Optional[bool] = None

class Channel(ChannelBase):
    id: int

    class Config:
        orm_mode = True