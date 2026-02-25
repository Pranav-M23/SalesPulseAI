from fastapi import HTTPException
import requests
import os
import logging

class SlackProvider:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL environment variable not set")

    def send_message(self, message: str):
        payload = {
            "text": message
        }
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send message to Slack")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")