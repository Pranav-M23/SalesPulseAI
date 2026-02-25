from typing import Any, Dict
import requests
from fastapi import HTTPException
from src.config.settings import SMS_PROVIDER_API_URL, SMS_PROVIDER_API_KEY

class SMSProvider:
    def __init__(self):
        self.api_url = SMS_PROVIDER_API_URL
        self.api_key = SMS_PROVIDER_API_KEY

    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        payload = {
            "to": to,
            "message": message,
            "api_key": self.api_key
        }
        response = requests.post(self.api_url, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("error", "Failed to send SMS"))

        return response.json()