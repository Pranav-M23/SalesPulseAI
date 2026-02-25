from fastapi import HTTPException, status


class SalesPulseException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class OpenAIServiceError(SalesPulseException):
    def __init__(self, message: str = "OpenAI service unavailable"):
        super().__init__(message=message, status_code=503)


class TwilioServiceError(SalesPulseException):
    def __init__(self, message: str = "Twilio service unavailable"):
        super().__init__(message=message, status_code=503)


class SendGridServiceError(SalesPulseException):
    def __init__(self, message: str = "SendGrid service unavailable"):
        super().__init__(message=message, status_code=503)


class WhatsAppCloudAPIError(SalesPulseException):
    def __init__(self, message: str = "WhatsApp Cloud API service unavailable"):
        super().__init__(message=message, status_code=503)


class DatabaseError(SalesPulseException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=500)


class ValidationError(SalesPulseException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=422)


def not_found(detail: str = "Resource not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
