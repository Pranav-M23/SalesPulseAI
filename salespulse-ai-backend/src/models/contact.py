from sqlalchemy import Column, Integer, String
from src.db.base import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    company = Column(String, index=True)
    created_at = Column(Integer)  # Timestamp for when the contact was created
    updated_at = Column(Integer)  # Timestamp for when the contact was last updated

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email}, phone={self.phone}, company={self.company})>"