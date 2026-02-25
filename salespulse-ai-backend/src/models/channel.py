from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(Enum('email', 'sms', 'whatsapp', name='channel_types'), index=True)
    api_key = Column(String, nullable=False)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive

    def __repr__(self):
        return f"<Channel(name={self.name}, type={self.type}, is_active={self.is_active})>"