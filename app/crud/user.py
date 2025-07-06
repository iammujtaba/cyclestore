from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional, Dict, Any

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create a new user"""
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    for field, value in user_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True
