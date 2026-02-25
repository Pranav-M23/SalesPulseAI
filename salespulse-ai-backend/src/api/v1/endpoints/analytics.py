from fastapi import APIRouter, HTTPException
from typing import List
from src.models.analytics import Analytics
from src.schemas.analytics import AnalyticsCreate, AnalyticsResponse
from src.services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.post("/analytics/", response_model=AnalyticsResponse)
async def create_analytics(analytics_data: AnalyticsCreate):
    try:
        return await analytics_service.create_analytics(analytics_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/", response_model=List[AnalyticsResponse])
async def get_analytics():
    try:
        return await analytics_service.get_all_analytics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))