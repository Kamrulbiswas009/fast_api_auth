from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base user schema
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=255)


# User registration request
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long")


# User login with JSON request
class UserLogin(BaseModel):
    username_or_email: str = Field(..., description="User username or email address")
    password: str = Field(...)


# User profile update
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None


# Change password request
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# User public response schema
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Authentication token schema
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Refresh token request
class TokenRefreshRequest(BaseModel):
    refresh_token: str


# Refresh token response
class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Generic message response
class MessageResponse(BaseModel):
    message: str
