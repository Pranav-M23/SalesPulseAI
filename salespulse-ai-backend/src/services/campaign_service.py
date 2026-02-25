from sqlalchemy.orm import Session
from models.campaign import Campaign
from schemas.campaign import CampaignCreate, CampaignUpdate
from core.exceptions import NotFoundException

class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        new_campaign = Campaign(**campaign_data.dict())
        self.db.add(new_campaign)
        self.db.commit()
        self.db.refresh(new_campaign)
        return new_campaign

    def get_campaign(self, campaign_id: int) -> Campaign:
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise NotFoundException(f"Campaign with id {campaign_id} not found")
        return campaign

    def update_campaign(self, campaign_id: int, campaign_data: CampaignUpdate) -> Campaign:
        campaign = self.get_campaign(campaign_id)
        for key, value in campaign_data.dict(exclude_unset=True).items():
            setattr(campaign, key, value)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete_campaign(self, campaign_id: int) -> None:
        campaign = self.get_campaign(campaign_id)
        self.db.delete(campaign)
        self.db.commit()