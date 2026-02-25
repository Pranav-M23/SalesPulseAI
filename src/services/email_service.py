from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from src.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import SendGridServiceError

_sg_client = None


def _get_client():
    global _sg_client
    if _sg_client is None:
        if not settings.SENDGRID_API_KEY:
            raise SendGridServiceError("SendGrid API key not configured")
        _sg_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    return _sg_client


async def send_email(to_email, subject, body, to_name=None, html=False):
    logger.info(f"Sending email to {to_email} subject='{subject}'")
    try:
        sg = _get_client()
        from_email = Email(settings.SENDGRID_FROM_EMAIL, "SalesPulse AI")
        to = To(to_email, to_name)
        content_type = "text/html" if html else "text/plain"
        content = Content(content_type, body)
        mail = Mail(from_email, to, subject, content)
        response = sg.send(mail)
        logger.info(f"Email sent: status_code={response.status_code}")
        message_id = response.headers.get("X-Message-Id", "")
        return {"message_id": message_id, "status_code": response.status_code}
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        raise SendGridServiceError(f"Failed to send email: {str(e)}")
