from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..models.user import User
from ..core.exceptions import UserNotFoundException

def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_id():
    # This function should extract the user ID from the request context (e.g., from a token)
    pass  # Implementation depends on your authentication method