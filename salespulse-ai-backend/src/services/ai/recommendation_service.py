from typing import List, Dict
import random

class RecommendationService:
    def __init__(self):
        self.recommendations = {
            "product": ["Product A", "Product B", "Product C"],
            "service": ["Service A", "Service B", "Service C"],
            "content": ["Content A", "Content B", "Content C"]
        }

    def get_recommendations(self, category: str, count: int = 3) -> List[str]:
        if category not in self.recommendations:
            raise ValueError("Invalid category. Choose from 'product', 'service', or 'content'.")
        
        return random.sample(self.recommendations[category], min(count, len(self.recommendations[category])))

    def generate_follow_up_message(self, lead_data: Dict) -> str:
        recommendations = self.get_recommendations(lead_data.get("interest_category", "product"))
        return f"Based on your interest in {lead_data.get('interest_category', 'products')}, we recommend: {', '.join(recommendations)}."