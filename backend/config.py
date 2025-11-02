from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "pole_wizard_forge"
    
    # JWT Configuration
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_in_days: int = 7
    
    # Email Configuration
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = "noreply@polewizard.com"
    
    # App Configuration
    app_url: str = "http://localhost:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration
    # Comma-separated list of allowed origins (e.g., "https://app.netlify.app,https://app2.netlify.app")
    # Or set ALLOWED_ORIGINS="*" to allow all origins (not recommended for production)
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:3000,http://127.0.0.1:8080"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    def get_cors_origins(self) -> List[str]:
        """Parse allowed_origins string into a list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

settings = Settings()
