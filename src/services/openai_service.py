import asyncio
from groq import Groq, APIError, RateLimitError, APIConnectionError
from src.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import OpenAIServiceError

# Initialize Groq client
_client = None

MODEL_PRIMARY = "llama-3.1-8b-instant"
MODEL_FALLBACK = "gemma2-9b-it"
MAX_RETRIES = 3
RETRY_DELAY = 2


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise OpenAIServiceError("Groq API key not configured")
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


async def _call_groq(messages, max_tokens=800, temperature=0.7):
    """Call Groq API with automatic retry and model fallback."""
    for attempt in range(MAX_RETRIES):
        model = MODEL_PRIMARY if attempt < 2 else MODEL_FALLBACK
        try:
            logger.info(f"Groq attempt {attempt + 1}/{MAX_RETRIES} with model={model}")
            client = _get_client()

            # Groq SDK is synchronous, run in thread pool
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()

        except RateLimitError as e:
            logger.warning(f"Groq rate limited (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (attempt + 1)
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                raise OpenAIServiceError("Groq rate limit exceeded. Please try again in a minute.")

        except APIConnectionError as e:
            logger.error(f"Groq connection error: {e}")
            raise OpenAIServiceError("Failed to connect to Groq API")

        except APIError as e:
            logger.error(f"Groq API error: {e}")
            raise OpenAIServiceError(f"Groq API error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected Groq error: {e}")
            raise OpenAIServiceError(f"Groq error: {str(e)}")


async def rewrite_message(draft_message, subject, cta, tone_instruction):
    """Use Groq to rewrite / polish a sales message."""
    logger.info("Requesting Groq rewrite...")
    prompt = (
        f"Rewrite the following sales email to make it more compelling and optimized for reply rates.\n\n"
        f"Tone instruction: {tone_instruction}\n\n"
        f"--- DRAFT SUBJECT ---\n{subject}\n\n"
        f"--- DRAFT BODY ---\n{draft_message}\n\n"
        f"--- DRAFT CTA ---\n{cta}\n\n"
        f"Return ONLY the result in this exact format:\n"
        f"SUBJECT: <improved subject>\n"
        f"BODY: <improved body>\n"
        f"CTA: <improved cta>"
    )

    messages = [
        {"role": "system", "content": settings.SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    content = await _call_groq(messages, max_tokens=800)
    return _parse_rewrite_response(content, subject, draft_message, cta)


async def chat_completion(messages):
    """Send a conversation to Groq and return the assistant reply."""
    logger.info(f"Groq chat completion with {len(messages)} messages")

    full_messages = [
        {"role": "system", "content": settings.SYSTEM_PROMPT},
        *messages,
    ]

    reply = await _call_groq(full_messages, max_tokens=500)
    logger.info(f"Groq reply length: {len(reply)} chars")
    return reply


def _parse_rewrite_response(content, fallback_subject, fallback_body, fallback_cta):
    """Parse the structured rewrite output."""
    subject = fallback_subject
    body = fallback_body
    cta = fallback_cta
    lines = content.split("\n")
    current_section = None
    body_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("SUBJECT:"):
            subject = stripped[len("SUBJECT:"):].strip()
            current_section = "subject"
        elif stripped.upper().startswith("BODY:"):
            body_text = stripped[len("BODY:"):].strip()
            if body_text:
                body_lines.append(body_text)
            current_section = "body"
        elif stripped.upper().startswith("CTA:"):
            cta = stripped[len("CTA:"):].strip()
            current_section = "cta"
        elif current_section == "body":
            body_lines.append(line)
    if body_lines:
        body = "\n".join(body_lines).strip()
    return {"subject": subject, "message": body, "cta": cta}
