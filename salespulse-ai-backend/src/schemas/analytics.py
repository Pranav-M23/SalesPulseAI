from pydantic import BaseModel
from typing import Optional, List

class AnalyticsBase(BaseModel):
    message_id: str
    channel: str
    status: str
    timestamp: str

class AnalyticsCreate(AnalyticsBase):
    pass

class Analytics(AnalyticsBase):
    id: int

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    analytics: List[Analytics]