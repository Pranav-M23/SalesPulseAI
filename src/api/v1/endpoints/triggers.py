from fastapi import APIRouter, Query
from typing import Optional
from src.schemas.trigger import (
    CreateTriggerRequest,
    TriggerResponse,
    TriggerListResponse,
    CreateDripCampaignRequest,
    DripCampaignResponse,
)
from src.services.trigger_service import (
    create_trigger,
    get_all_triggers,
    cancel_trigger,
    cancel_campaign,
)
from src.core.logging import logger

router = APIRouter()


@router.post("/triggers", response_model=TriggerResponse)
async def create_trigger_endpoint(request: CreateTriggerRequest):
    """Create a new automated trigger."""
    logger.info(f"Creating trigger: {request.name} type={request.trigger_type}")
    result = await create_trigger(
        name=request.name,
        trigger_type=request.trigger_type.value,
        channel=request.channel.value,
        recipient=request.recipient,
        recipient_name=request.recipient_name,
        message=request.message,
        subject=request.subject,
        delay_minutes=request.delay_minutes,
        max_retries=request.max_retries,
        stop_on_reply=request.stop_on_reply,
    )
    return TriggerResponse(
        success=True,
        trigger_id=result["trigger_id"],
        name=result["name"],
        trigger_type=result["trigger_type"],
        channel=result["channel"],
        recipient=result["recipient"],
        status=result["status"],
        delay_minutes=result["delay_minutes"],
        scheduled_at=result["scheduled_at"],
        detail="Trigger created successfully",
    )


@router.get("/triggers", response_model=TriggerListResponse)
async def list_triggers(status: Optional[str] = Query(None)):
    """List all triggers."""
    triggers = await get_all_triggers(status=status)
    return TriggerListResponse(success=True, total=len(triggers), triggers=triggers)


@router.delete("/triggers/{trigger_id}")
async def cancel_trigger_endpoint(trigger_id: int):
    """Cancel a specific trigger."""
    return await cancel_trigger(trigger_id)


@router.post("/triggers/drip-campaign", response_model=DripCampaignResponse)
async def create_drip_campaign(request: CreateDripCampaignRequest):
    """Create a multi-step drip campaign."""
    logger.info(f"Creating drip campaign: {request.name} steps={len(request.messages)}")
    trigger_ids = []

    for i, message in enumerate(request.messages):
        delay = request.delay_between_minutes * (i + 1)
        subject = f"{request.subject_prefix} - Step {i + 1}" if request.subject_prefix else None

        result = await create_trigger(
            name=f"{request.name} - Step {i + 1}",
            trigger_type="drip",
            channel=request.channel.value,
            recipient=request.recipient,
            recipient_name=request.recipient_name,
            message=message,
            subject=subject,
            delay_minutes=delay,
            max_retries=3,
            stop_on_reply=request.stop_on_reply,
            campaign_name=request.name,
            step_number=i + 1,
        )
        trigger_ids.append(result["trigger_id"])

    return DripCampaignResponse(
        success=True,
        campaign_name=request.name,
        total_steps=len(request.messages),
        trigger_ids=trigger_ids,
        detail=f"Drip campaign created with {len(request.messages)} steps",
    )


@router.delete("/triggers/campaign/{campaign_name}")
async def cancel_campaign_endpoint(campaign_name: str):
    """Cancel all triggers in a campaign."""
    return await cancel_campaign(campaign_name)


