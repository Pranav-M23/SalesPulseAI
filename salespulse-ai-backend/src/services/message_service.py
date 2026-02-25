from sqlalchemy.orm import Session
from models.message import Message
from schemas.message import MessageCreate
from core.exceptions import NotFoundException

class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message_data: MessageCreate) -> Message:
        new_message = Message(**message_data.dict())
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        return new_message

    def get_message(self, message_id: int) -> Message:
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise NotFoundException(f"Message with id {message_id} not found")
        return message

    def delete_message(self, message_id: int) -> None:
        message = self.get_message(message_id)
        self.db.delete(message)
        self.db.commit()