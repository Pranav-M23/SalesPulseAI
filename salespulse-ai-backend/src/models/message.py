from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, nullable=False)
    recipient_id = Column(Integer, nullable=False)
    channel = Column(String, nullable=False)
    created_at = Column(Integer, nullable=False)  # Timestamp for when the message was created
    updated_at = Column(Integer, nullable=True)   # Timestamp for when the message was last updated

    def __repr__(self):
        return f"<Message(id={self.id}, content={self.content}, sender_id={self.sender_id}, recipient_id={self.recipient_id}, channel={self.channel})>"