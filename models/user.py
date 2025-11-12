"""User model and schemas."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid
import re

def generate_ocid() -> str:
    """Generate custom unique ID like gocid-usr-<uuid>."""
    return f"gocid-usr-{str(uuid.uuid4())}"

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class UserInDB(UserBase):
    """User schema as stored in database."""
    ocid: str = Field(default_factory=generate_ocid)
    password_hash: str
    reset_token: Optional[str] = None  # Keep for backward compatibility
    reset_token_expiry: Optional[datetime] = None
    reset_code: Optional[str] = None  # 6-digit code
    reset_code_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(UserBase):
    """Schema for user response (public data)."""
    ocid: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    """Schema for verifying reset code."""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is 6 digits."""
        if not v.isdigit():
            raise ValueError('Code must be 6 digits')
        if len(v) != 6:
            raise ValueError('Code must be exactly 6 digits')
        return v

class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is 6 digits."""
        if not v.isdigit():
            raise ValueError('Code must be 6 digits')
        if len(v) != 6:
            raise ValueError('Code must be exactly 6 digits')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str

