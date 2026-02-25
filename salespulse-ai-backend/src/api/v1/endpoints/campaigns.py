from fastapi import APIRouter, HTTPException
from typing import List
from src.models.campaign import Campaign
from src.schemas.campaign import CampaignCreate, CampaignUpdate
from src.services.campaign_service import CampaignService

router = APIRouter()
campaign_service = CampaignService()

@router.post("/", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    return await campaign_service.create_campaign(campaign)

@router.get("/", response_model=List[Campaign])
async def get_campaigns():
    return await campaign_service.get_all_campaigns()

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: int):
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: int, campaign: CampaignUpdate):
    updated_campaign = await campaign_service.update_campaign(campaign_id, campaign)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

@router.delete("/{campaign_id}", response_model=dict)
async def delete_campaign(campaign_id: int):
    success = await campaign_service.delete_campaign(campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}