from fastapi import HTTPException
import requests
import os
import logging

class WhatsAppProvider:
    def __init__(self):
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.api_key = os.getenv("WHATSAPP_API_KEY")
        self.logger = logging.getLogger(__name__)

    def send_message(self, to: str, message: str):
        payload = {
            "to": to,
            "message": message
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            self.logger.info(f"Message sent to {to}: {message}")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred: {http_err}")
            raise HTTPException(status_code=response.status_code, detail=str(http_err))
        except Exception as err:
            self.logger.error(f"An error occurred: {err}")
            raise HTTPException(status_code=500, detail="An error occurred while sending the message")