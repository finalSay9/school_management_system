# routers/auth.py - Authentication Routes
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from schemas import CreateUser, UserResponse, Token, LoginRequest, TokenData
from models import User
import users
from security import(
    verify_password, 
    create_access_token,
     create_refresh_token, 
     verify_token)
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer




security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
     # Import here to avoid circular imports
    
    user_id = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Update last seen
    user.last_seen_at = datetime.utcnow()
    db.commit()
    
    return user


@router.post("/register", response_model=UserResponse)
def register(user: CreateUser, db: Session = Depends(get_db)):
    """Register a new user"""
    return users.create_user(db, user)

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return tokens"""
    # Query user by email (assuming username_or_email is email)
    user = db.query(User).filter(User.email == login_data.username_or_email).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token"""
    user_id = verify_token(refresh_token, "refresh")
    user = users.get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }