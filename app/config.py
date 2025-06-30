import os

class Settings:
    PROJECT_NAME: str = "Supreme Cycle and Rickshaw Company"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cyclestore.db")
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"

settings = Settings()
