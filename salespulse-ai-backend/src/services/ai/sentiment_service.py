from typing import Dict, Any
from fastapi import HTTPException
from transformers import pipeline

class SentimentService:
    def __init__(self):
        self.sentiment_pipeline = pipeline("sentiment-analysis")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        if not text:
            raise HTTPException(status_code=400, detail="Text input is required for sentiment analysis.")
        
        result = self.sentiment_pipeline(text)
        return result[0]  # Return the first result from the pipeline

sentiment_service = SentimentService()