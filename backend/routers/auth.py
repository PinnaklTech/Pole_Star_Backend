"""Authentication routes - signup, login, logout, forgot password, reset password."""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from database import get_database
from models.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse,
    UserInDB
)
from utils.security import (
    hash_password, verify_password, create_access_token,
    generate_reset_token, verify_reset_token
)
from utils.email import send_password_reset_email, send_welcome_email
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user."""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    user_dict = UserInDB(
        email=user_data.email.lower(),
        name=user_data.name,
        password_hash=hash_password(user_data.password)
    ).dict()
    
    # Insert user into database
    try:
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        # Send welcome email (non-blocking)
        try:
            await send_welcome_email(user_data.email, user_data.name)
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {e}")
        
        # Create access token
        access_token = create_access_token(data={"sub": user_dict["ocid"]})
        
        # Return response
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                ocid=user_dict["ocid"],
                email=user_dict["email"],
                name=user_dict["name"],
                created_at=user_dict["created_at"]
            )
        )
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token."""
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": credentials.email.lower()})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["ocid"]})
    
    # Return response
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            ocid=user["ocid"],
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
    )

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (client should remove token).
    In a stateless JWT system, logout is handled client-side.
    This endpoint mainly validates that the user is authenticated.
    """
    return MessageResponse(message="Successfully logged out")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        ocid=current_user["ocid"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"]
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Send password reset email to user.
    Returns generic message regardless of whether user exists (security).
    """
    db = get_database()
    
    # Always return success message (don't reveal if email exists)
    generic_message = "If an account exists with this email, you will receive a password reset link shortly."
    
    # Find user by email
    user = await db.users.find_one({"email": request.email.lower()})
    
    if not user:
        # Don't reveal that user doesn't exist
        logger.info(f"Password reset requested for non-existent email: {request.email}")
        return MessageResponse(message=generic_message)
    
    # Generate reset token
    reset_token = generate_reset_token()
    reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    
    # Update user with reset token
    await db.users.update_one(
        {"email": request.email.lower()},
        {
            "$set": {
                "reset_token": reset_token,
                "reset_token_expiry": reset_token_expiry,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send reset email
    try:
        await send_password_reset_email(
            to_email=user["email"],
            reset_token=reset_token,
            user_name=user["name"]
        )
        logger.info(f"Password reset email sent to {user['email']}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        # Still return success to user (don't reveal internal errors)
    
    return MessageResponse(message=generic_message)

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset user password with valid token."""
    db = get_database()
    
    # Find user with matching reset token
    user = await db.users.find_one({"reset_token": request.token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Verify token and expiry
    if not verify_reset_token(
        request.token,
        user.get("reset_token"),
        user.get("reset_token_expiry", datetime.utcnow())
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password and clear reset token
    await db.users.update_one(
        {"ocid": user["ocid"]},
        {
            "$set": {
                "password_hash": hash_password(request.new_password),
                "updated_at": datetime.utcnow()
            },
            "$unset": {
                "reset_token": "",
                "reset_token_expiry": ""
            }
        }
    )
    
    logger.info(f"Password reset successful for user: {user['email']}")
    
    return MessageResponse(message="Password reset successful. You can now log in with your new password.")

@router.post("/verify", response_model=MessageResponse)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the current JWT token is valid."""
    return MessageResponse(message="Token is valid")
