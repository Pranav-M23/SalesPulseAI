from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Analytics(Base):
    __tablename__ = 'analytics'

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, index=True)
    channel = Column(String, index=True)
    response_time = Column(Float)
    success = Column(Integer)  # 1 for success, 0 for failure
    created_at = Column(String)  # Use appropriate type for your timestamp

    def __repr__(self):
        return f"<Analytics(id={self.id}, message_id={self.message_id}, channel='{self.channel}', response_time={self.response_time}, success={self.success})>"