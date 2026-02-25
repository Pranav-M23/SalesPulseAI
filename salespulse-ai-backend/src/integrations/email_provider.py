from fastapi import HTTPException
from pydantic import BaseModel
import os
import sendgrid
from sendgrid.helpers.mail import Mail

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    content: str

class EmailProvider:
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sg_client = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

    def send_email(self, email_request: EmailRequest):
        message = Mail(
            from_email=os.getenv("FROM_EMAIL"),
            to_emails=email_request.to_email,
            subject=email_request.subject,
            plain_text_content=email_request.content
        )
        try:
            response = self.sg_client.send(message)
            return response.status_code
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))