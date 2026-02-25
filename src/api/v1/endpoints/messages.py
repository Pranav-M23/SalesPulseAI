from fastapi import APIRouter
from src.schemas.message import GenerateMessageRequest, GenerateMessageResponse
from src.services.template_engine import render_template
from src.services.scoring_engine import score_message
from src.services.openai_service import rewrite_message
from src.services.conversation_service import store_generated_message
from src.core.logging import logger

router = APIRouter()


@router.post("/generate-message", response_model=GenerateMessageResponse)
async def generate_message(request: GenerateMessageRequest):
    logger.info(f"Generating message for lead={request.name} company={request.company} stage={request.stage}")

    rendered = render_template(
        name=request.name,
        role=request.role,
        company=request.company,
        industry=request.industry,
        pain_point=request.pain_point,
        stage=request.stage,
        tone=request.tone,
    )

    subject = rendered["subject"]
    body = rendered["body"]
    cta = rendered["cta"]

    if request.use_ai_rewrite:
        logger.info("AI rewrite enabled -- calling OpenAI")
        rewritten = await rewrite_message(
            draft_message=body,
            subject=subject,
            cta=cta,
            tone_instruction=rendered["tone_instruction"],
        )
        subject = rewritten["subject"]
        body = rewritten["message"]
        cta = rewritten["cta"]

    msg_score = score_message(
        message=body,
        subject=subject,
        cta=cta,
        stage=request.stage,
        tone=request.tone,
    )

    await store_generated_message(
        lead_name=request.name,
        lead_company=request.company,
        stage=request.stage.value,
        subject=subject,
        message=body,
        cta=cta,
        score=msg_score,
    )

    return GenerateMessageResponse(
        success=True,
        subject=subject,
        message=body,
        cta=cta,
        score=msg_score,
        stage=request.stage.value,
        tone=request.tone.value,
    )
