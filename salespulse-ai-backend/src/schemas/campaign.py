from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    target_audience: List[str]

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int

    class Config:
        orm_mode = True