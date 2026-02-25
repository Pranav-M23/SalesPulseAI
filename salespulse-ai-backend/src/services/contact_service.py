from sqlalchemy.orm import Session
from models.contact import Contact
from schemas.contact import ContactCreate, ContactUpdate
from core.exceptions import NotFoundException

class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def create_contact(self, contact: ContactCreate) -> Contact:
        db_contact = Contact(**contact.dict())
        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact

    def get_contact(self, contact_id: int) -> Contact:
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise NotFoundException(f"Contact with id {contact_id} not found")
        return contact

    def update_contact(self, contact_id: int, contact_data: ContactUpdate) -> Contact:
        contact = self.get_contact(contact_id)
        for key, value in contact_data.dict(exclude_unset=True).items():
            setattr(contact, key, value)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, contact_id: int) -> None:
        contact = self.get_contact(contact_id)
        self.db.delete(contact)
        self.db.commit()