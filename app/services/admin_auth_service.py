"""
Admin Authentication Service for Supreme Cycle & Rickshaw Company
Handles admin login, session management
"""

from sqlalchemy.orm import Session
from app.models.admin import Admin, AdminSession
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import secrets

class AdminAuthService:
    """Service for handling admin authentication"""
    
    def __init__(self):
        self.session_duration = timedelta(hours=24)  # Admin session expires in 24 hours
    
    def authenticate_admin(self, db: Session, username: str, password: str) -> Optional[Admin]:
        """Authenticate admin with username and password"""
        admin = db.query(Admin).filter(
            Admin.username == username,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return None
        
        if not admin.verify_password(password):
            return None
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.commit()
        
        return admin
    
    def create_session(self, db: Session, admin: Admin, request: Request) -> str:
        """Create a new admin session"""
        
        # Deactivate existing sessions for this admin
        db.query(AdminSession).filter(
            AdminSession.admin_id == admin.id,
            AdminSession.is_active == True
        ).update({"is_active": False})
        
        # Create new session
        session_token = AdminSession.generate_token()
        expires_at = datetime.utcnow() + self.session_duration
        
        session = AdminSession(
            admin_id=admin.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")
        )
        
        db.add(session)
        db.commit()
        
        return session_token
    
    def get_current_admin(self, db: Session, session_token: str) -> Optional[Admin]:
        """Get current admin from session token"""
        if not session_token:
            return None
        
        # Find active session
        session = db.query(AdminSession).filter(
            AdminSession.session_token == session_token,
            AdminSession.is_active == True,
            AdminSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Get admin
        admin = db.query(Admin).filter(Admin.id == session.admin_id).first()
        
        if not admin or not admin.is_active:
            return None
        
        return admin
    
    def logout_admin(self, db: Session, session_token: str) -> bool:
        """Logout admin by deactivating session"""
        session = db.query(AdminSession).filter(
            AdminSession.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    def invalidate_session(self, db: Session, session_token: str) -> bool:
        """Invalidate admin session"""
        return self.logout_admin(db, session_token)
    
    def create_default_admin(self, db: Session) -> Admin:
        """Create default admin if not exists"""
        # Check for both admin and superuser
        existing_admin = db.query(Admin).filter(
            (Admin.username == "admin") | (Admin.username == "superuser")
        ).first()

        if existing_admin:
            return existing_admin

        # Create default admin with standard credentials
        admin = Admin(
            username="admin",
            hashed_password=Admin.hash_password("admin123"),
            full_name="Administrator",
            email="admin@supremecycle.com",
            is_super_admin=True
        )

        try:
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✓ Created default admin user: {admin.username}")
            return admin
        except Exception as e:
            db.rollback()
            print(f"✗ Failed to create admin: {e}")
            raise

# Create global instance
admin_auth_service = AdminAuthService()
