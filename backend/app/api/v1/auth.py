from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, User, Token, UserLogin
from app.services.auth_service import AuthService
from app.db.mongodb import get_database
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db = Depends(get_database)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database connection
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists
    """
    service = AuthService(db)
    return await service.create_user(user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db = Depends(get_database)
):
    """
    Login and get access tokens.
    
    Args:
        form_data: OAuth2 password form with username (email) and password
        db: Database connection
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    service = AuthService(db)
    return await service.authenticate_user(form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db = Depends(get_database)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Valid refresh token
        db: Database connection
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    service = AuthService(db)
    return await service.refresh_access_token(refresh_token)


@router.get("/me", response_model=User)
async def get_current_user(
    user: User = Depends(AuthService.get_current_user)
):
    """
    Get current authenticated user profile.
    
    Args:
        user: Current user from token
        
    Returns:
        User profile data
    """
    return user
