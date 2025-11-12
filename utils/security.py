"""Security utilities for password hashing and JWT token management."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings
import secrets

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_expires_in_days)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None

def generate_reset_token() -> str:
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)

def verify_reset_token(token: str, stored_token: str, expiry: datetime) -> bool:
    """Verify a password reset token."""
    if not token or not stored_token:
        return False
    
    if token != stored_token:
        return False
    
    if datetime.utcnow() > expiry:
        return False
    
    return True

def generate_reset_code() -> str:
    """Generate a 6-digit security code for password reset."""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def verify_reset_code(code: str, stored_code: str, expiry: datetime) -> bool:
    """Verify a password reset code."""
    if not code or not stored_code:
        return False
    
    # Code should be exactly 6 digits
    if not code.isdigit() or len(code) != 6:
        return False
    
    if code != stored_code:
        return False
    
    if datetime.utcnow() > expiry:
        return False
    
    return True

