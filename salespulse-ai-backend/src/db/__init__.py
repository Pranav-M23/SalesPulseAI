# __init__.py file for the db module

from .session import SessionLocal, engine
from .base import Base

# Create the database tables
def init_db():
    Base.metadata.create_all(bind=engine)