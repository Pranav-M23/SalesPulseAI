from sqlalchemy.orm import Session
from models.analytics import Analytics
from schemas.analytics import AnalyticsCreate, AnalyticsUpdate
from core.exceptions import NotFoundException

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def create_analytics(self, analytics_data: AnalyticsCreate) -> Analytics:
        analytics = Analytics(**analytics_data.dict())
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(analytics)
        return analytics

    def get_analytics(self, analytics_id: int) -> Analytics:
        analytics = self.db.query(Analytics).filter(Analytics.id == analytics_id).first()
        if not analytics:
            raise NotFoundException(f"Analytics with id {analytics_id} not found")
        return analytics

    def update_analytics(self, analytics_id: int, analytics_data: AnalyticsUpdate) -> Analytics:
        analytics = self.get_analytics(analytics_id)
        for key, value in analytics_data.dict(exclude_unset=True).items():
            setattr(analytics, key, value)
        self.db.commit()
        self.db.refresh(analytics)
        return analytics

    def delete_analytics(self, analytics_id: int) -> None:
        analytics = self.get_analytics(analytics_id)
        self.db.delete(analytics)
        self.db.commit()