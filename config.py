from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "pole_wizard_forge"
    
    # JWT Configuration
    jwt_secret: str = "your-secret-key-change-in-production"  # MUST be changed in production!
    jwt_algorithm: str = "HS256"
    jwt_expires_in_days: int = 7
    
    # Email Configuration (Hostinger SMTP)
    # These values can be overridden in .env file
    email_host: str = "smtp.hostinger.com"
    email_port: int = 465  # 465 for SSL, 587 for STARTTLS (Hostinger supports both)
    email_user: str = ""
    email_password: str = ""
    email_from: str = "noreply.polestar@pinnakltech.com"
    
    # App Configuration
    app_url: str = "http://localhost:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration - comma-separated list of allowed origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    
    # Security Configuration
    max_request_size: int = 10 * 1024 * 1024  # 10MB default
    rate_limit_per_minute: int = 60  # Requests per minute per IP
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable."""
        if self.cors_origins:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return ["http://localhost:5173"]  # Fallback
    
    def validate_production_settings(self) -> List[str]:
        """Validate that production settings are properly configured."""
        warnings = []
        
        if self.is_production:
            if self.jwt_secret == "your-secret-key-change-in-production":
                warnings.append("CRITICAL: JWT_SECRET must be changed from default value!")
            
            if self.app_url.startswith("http://localhost"):
                warnings.append("WARNING: APP_URL is set to localhost in production!")
            
            if self.mongodb_uri.startswith("mongodb://localhost"):
                warnings.append("WARNING: MongoDB URI points to localhost in production!")
            
            if self.debug:
                warnings.append("WARNING: Debug mode is enabled in production!")
        
        return warnings

settings = Settings()

# Validate production settings on startup
if settings.is_production:
    warnings = settings.validate_production_settings()
    if warnings:
        import sys
        print("\n" + "="*60, file=sys.stderr)
        print("⚠️  PRODUCTION CONFIGURATION WARNINGS:", file=sys.stderr)
        print("="*60, file=sys.stderr)
        for warning in warnings:
            print(f"  ❌ {warning}", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
