import httpx
from src.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import WhatsAppCloudAPIError

WHAPI_API_BASE = "https://gate.whapi.cloud"

_http_client = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        api_token = settings.META_WHATSAPP_ACCESS_TOKEN
        if not api_token:
            raise WhatsAppCloudAPIError("Whapi API token not configured")
        _http_client = httpx.AsyncClient(
            base_url=WHAPI_API_BASE,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    return _http_client


def _format_phone(to: str) -> str:
    """Format phone number for Whapi: strip +, whatsapp: prefix, return digits only."""
    return to.replace("whatsapp:", "").replace("+", "").replace(" ", "").strip()


async def send_whatsapp(to: str, message: str) -> dict:
    """Send a WhatsApp text message via Whapi.

    Args:
        to: Phone number in international format (e.g. +919876543210)
        message: Text message body

    Returns:
        dict with message_id and status
    """
    clean_number = _format_phone(to)

    payload = {
        "to": f"{clean_number}@s.whatsapp.net",
        "body": message,
    }

    logger.info(f"Sending WhatsApp via Whapi to {clean_number}")

    try:
        client = _get_client()
        response = await client.post("/messages/text", json=payload)

        if response.status_code not in (200, 201):
            error_msg = response.text
            try:
                error_data = response.json()
                error_msg = error_data.get("message", error_msg)
            except Exception:
                pass
            logger.error(f"Whapi error: {response.status_code} - {error_msg}")
            raise WhatsAppCloudAPIError(f"Whapi error: {error_msg}")

        data = response.json()
        message_id = data.get("message", {}).get("id", data.get("id", "unknown"))
        logger.info(f"WhatsApp sent via Whapi: id={message_id}")
        return {"message_id": message_id, "status": "sent"}

    except WhatsAppCloudAPIError:
        raise
    except httpx.TimeoutException:
        logger.error("Whapi request timed out")
        raise WhatsAppCloudAPIError("Whapi request timed out")
    except Exception as e:
        logger.error(f"Whapi error: {e}")
        raise WhatsAppCloudAPIError(f"Failed to send WhatsApp via Whapi: {str(e)}")


async def send_image(to: str, image_url: str, caption: str = None) -> dict:
    """Send an image message via Whapi."""
    clean_number = _format_phone(to)
    payload = {
        "to": f"{clean_number}@s.whatsapp.net",
        "media": {"url": image_url},
    }
    if caption:
        payload["caption"] = caption

    try:
        client = _get_client()
        response = await client.post("/messages/image", json=payload)
        if response.status_code not in (200, 201):
            raise WhatsAppCloudAPIError(f"Whapi image error: {response.text}")
        data = response.json()
        message_id = data.get("message", {}).get("id", "unknown")
        return {"message_id": message_id, "status": "sent"}
    except WhatsAppCloudAPIError:
        raise
    except Exception as e:
        raise WhatsAppCloudAPIError(f"Failed to send image via Whapi: {str(e)}")


async def mark_message_read(message_id: str) -> bool:
    """Mark a received message as read."""
    try:
        client = _get_client()
        response = await client.put(
            f"/messages/{message_id}",
            json={"status": "read"},
        )
        return response.status_code in (200, 201)
    except Exception as e:
        logger.error(f"Failed to mark message as read: {e}")
        return False


async def close_client():
    """Close the HTTP client (call on app shutdown)."""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None
