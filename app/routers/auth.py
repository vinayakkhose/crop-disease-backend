"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.schemas import UserCreate, UserResponse, Token, LoginResponse
from app.services.auth import (
    create_user, authenticate_user, create_access_token,
    verify_token, get_user_by_email
)
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    try:
        user = await create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            region=user_data.region,
            phone=user_data.phone
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            region=user.region,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login(email: str = Form(...), password: str = Form(...)):
    """Login user - returns token and user so client doesn't need a separate /me call."""
    email = (email or "").strip().lower()
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            region=user.region,
            created_at=user.created_at,
        ),
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    email = payload.get("sub")
    
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user = await get_user_by_email(current_user["email"])
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        region=user.region,
        created_at=user.created_at
    )
