from src.schemas.message import SalesStage, MessageTone
from src.core.logging import logger


def score_message(message, subject, cta, stage, tone):
    score = 50.0

    word_count = len(message.split())
    if 40 <= word_count <= 120:
        score += 10
    elif word_count < 20:
        score -= 10
    elif word_count > 200:
        score -= 15

    subject_words = len(subject.split())
    if 4 <= subject_words <= 12:
        score += 8
    elif subject_words > 15:
        score -= 5

    personalization_keywords = ["you", "your", "you're", "yourself"]
    personalization_count = sum(
        1 for w in message.lower().split() if w.strip(".,!?") in personalization_keywords
    )
    score += min(personalization_count * 2, 10)

    strong_cta_words = ["book", "schedule", "sign", "start", "reply", "call", "register", "join", "try"]
    if any(word in cta.lower() for word in strong_cta_words):
        score += 8

    if "?" in message:
        score += 5

    stage_bonuses = {
        SalesStage.CLOSING: 5,
        SalesStage.NEGOTIATION: 3,
        SalesStage.PROPOSAL: 3,
        SalesStage.RE_ENGAGEMENT: 2,
    }
    score += stage_bonuses.get(stage, 0)

    if tone == MessageTone.URGENT and any(w in message.lower() for w in ["today", "now", "limited", "deadline", "asap"]):
        score += 5
    if tone == MessageTone.CONSULTATIVE and "?" in message:
        score += 3

    spam_words = ["free", "guarantee", "act now", "click here", "no obligation", "winner"]
    spam_count = sum(1 for w in spam_words if w in message.lower())
    score -= spam_count * 5

    score = max(0.0, min(100.0, round(score, 1)))
    logger.info(f"Message score: {score}")
    return score
