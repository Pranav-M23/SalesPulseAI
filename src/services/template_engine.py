from src.schemas.message import SalesStage, MessageTone
from src.core.logging import logger

TEMPLATES = {
    SalesStage.PROSPECTING: {
        "subject": "Quick question about {company}'s {industry} strategy",
        "body": (
            "Hi {name},\n\n"
            "I came across {company} and noticed your work in the {industry} space. "
            "Many {role}s I speak with mention challenges around {pain_point}.\n\n"
            "We've helped similar companies tackle this -- would you be open to a brief chat this week?"
        ),
        "cta": "Book a 15-minute discovery call",
    },
    SalesStage.QUALIFICATION: {
        "subject": "Following up on our conversation, {name}",
        "body": (
            "Hi {name},\n\n"
            "Great speaking with you about {company}'s goals. "
            "You mentioned {pain_point} as a top priority -- "
            "I've put together a few ideas I think you'll find valuable.\n\n"
            "When would be a good time to walk through them?"
        ),
        "cta": "Schedule a solution walkthrough",
    },
    SalesStage.PROPOSAL: {
        "subject": "Proposal for {company} -- addressing {pain_point}",
        "body": (
            "Hi {name},\n\n"
            "Attached is a tailored proposal for {company} that directly addresses {pain_point}. "
            "The solution is designed specifically for {industry} teams.\n\n"
            "I'd love to discuss any questions you have -- are you free this week?"
        ),
        "cta": "Review proposal and schedule a call",
    },
    SalesStage.NEGOTIATION: {
        "subject": "Let's finalize the details, {name}",
        "body": (
            "Hi {name},\n\n"
            "We're excited about the potential partnership with {company}. "
            "I wanted to check in on the proposal and see if there are any remaining "
            "questions around {pain_point} or terms.\n\n"
            "Happy to hop on a quick call to iron out the details."
        ),
        "cta": "Finalize agreement this week",
    },
    SalesStage.CLOSING: {
        "subject": "Ready to get started, {name}?",
        "body": (
            "Hi {name},\n\n"
            "Everything looks aligned for {company} to move forward. "
            "Addressing {pain_point} is within reach -- let's lock in the next steps.\n\n"
            "I've prepared the onboarding details for your review."
        ),
        "cta": "Sign and start onboarding today",
    },
    SalesStage.FOLLOW_UP: {
        "subject": "Checking in, {name}",
        "body": (
            "Hi {name},\n\n"
            "I wanted to follow up on our last conversation about {pain_point} at {company}. "
            "Have you had a chance to review the information?\n\n"
            "I'm here if you have any questions -- happy to help."
        ),
        "cta": "Reply to reconnect",
    },
    SalesStage.RE_ENGAGEMENT: {
        "subject": "It's been a while, {name} -- any updates at {company}?",
        "body": (
            "Hi {name},\n\n"
            "I hope things are going well at {company}! "
            "I know {pain_point} was a focus area when we last spoke. "
            "We've since added new capabilities that might be a great fit for your {industry} team.\n\n"
            "Would you be open to a quick catch-up?"
        ),
        "cta": "Reopen the conversation",
    },
}

TONE_MODIFIERS = {
    MessageTone.FORMAL: "Use a professional and formal tone. Avoid contractions and slang.",
    MessageTone.FRIENDLY: "Use a warm, conversational tone. Be approachable.",
    MessageTone.URGENT: "Convey urgency. Emphasize time-sensitivity and scarcity.",
    MessageTone.CONSULTATIVE: "Position yourself as an advisor. Ask insightful questions.",
    MessageTone.CASUAL: "Keep it light and casual. Use a relaxed tone.",
}


def render_template(name, role, company, industry, pain_point, stage, tone):
    logger.info(f"Rendering template for stage={stage} tone={tone} lead={name}")
    template = TEMPLATES.get(stage, TEMPLATES[SalesStage.FOLLOW_UP])
    context = {
        "name": name,
        "role": role,
        "company": company,
        "industry": industry,
        "pain_point": pain_point,
    }
    subject = template["subject"].format(**context)
    body = template["body"].format(**context)
    cta = template["cta"]
    return {
        "subject": subject,
        "body": body,
        "cta": cta,
        "tone_instruction": TONE_MODIFIERS.get(tone, ""),
    }
