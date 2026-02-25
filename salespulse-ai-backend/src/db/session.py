from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()