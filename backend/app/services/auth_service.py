from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status, Depends
from app.models.user import UserCreate, User, Token, UserInDB
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user_id
)
from app.db.mongodb import get_database
from bson import ObjectId


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db["users"]
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        existing_user = await self.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user document
        user_dict = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": get_password_hash(user_data.password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.users_collection.insert_one(user_dict)
        
        # Return created user
        return User(
            id=str(result.inserted_id),
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=True,
            created_at=user_dict["created_at"]
        )
    
    async def authenticate_user(self, email: str, password: str) -> Token:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Access and refresh tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        user = await self.users_collection.find_one({"email": email})
        
        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )
        
        # Create tokens
        user_id = str(user["_id"])
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access and refresh tokens
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return None
        
        return User(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            is_active=user.get("is_active", True),
            created_at=user["created_at"]
        )
    
    @staticmethod
    async def get_current_user(
        user_id: str = Depends(get_current_user_id),
        db = Depends(get_database)
    ) -> User:
        """
        Dependency to get current authenticated user.
        
        Args:
            user_id: User ID from token
            db: Database connection
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If user not found
        """
        service = AuthService(db)
        user = await service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
