import os
from typing import Optional

class Settings:
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cyclestore.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "app/static/images/products")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def docs_url(self) -> Optional[str]:
        return None if self.is_production else "/docs"
    
    @property
    def redoc_url(self) -> Optional[str]:
        return None if self.is_production else "/redoc"

settings = Settings()
