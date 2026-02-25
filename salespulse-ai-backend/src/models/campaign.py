from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base

class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)  # e.g., 'active', 'paused', 'completed'
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    contacts = relationship("Contact", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(name={self.name}, status={self.status})>"