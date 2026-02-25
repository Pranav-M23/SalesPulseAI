from typing import Any, Dict
import openai
from fastapi import HTTPException
from src.config.settings import settings

class NLPService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_message(self, lead_data: Dict[str, Any]) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Generate a follow-up message for the lead data: {lead_data}"}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))