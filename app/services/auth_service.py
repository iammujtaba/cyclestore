"""
Authentication Service for Supreme Cycle & Rickshaw Company
Handles user registration, login, session management
"""

from sqlalchemy.orm import Session
from app.models.user import User, UserSession
from app.db.session import get_db
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import secrets

class AuthService:
    """Service for handling user authentication"""
    
    def __init__(self):
        self.session_duration = timedelta(days=30)  # Session expires in 30 days
    
    def register_user(self, db: Session, user_data: dict) -> User:
        """Register a new user"""
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data['email']).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data['username']).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = User.hash_password(user_data['password'])
        db_user = User(
            email=user_data['email'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            hashed_password=hashed_password,
            phone=user_data.get('phone'),
            address=user_data.get('address'),
            city=user_data.get('city'),
            state=user_data.get('state'),
            pincode=user_data.get('pincode')
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not user.verify_password(password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    def create_session(self, db: Session, user: User, request: Request) -> str:
        """Create a new session for the user"""
        
        # Generate session token
        session_token = UserSession.generate_token()
        expires_at = datetime.utcnow() + self.session_duration
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # Create session record
        db_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(db_session)
        db.commit()
        
        return session_token
    
    def get_current_user(self, db: Session, session_token: str) -> Optional[User]:
        """Get current user from session token"""
        if not session_token:
            return None
        
        # Find active session
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        
        if not user or not user.is_active:
            return None
        
        return user
    
    def logout_user(self, db: Session, session_token: str) -> bool:
        """Logout user by deactivating session"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    def cleanup_expired_sessions(self, db: Session):
        """Clean up expired sessions"""
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        )
        expired_sessions.update({"is_active": False})
        db.commit()

# Create global instance
auth_service = AuthService()
