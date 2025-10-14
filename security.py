import hashlib
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
import os
from dotenv import load_dotenv
from models import User
from database import get_db


security = HTTPBearer()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-for-testing")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Always hash long passwords with SHA256 first to stay within bcrypt's 72-byte limit
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # Use SHA256 to reduce the password to a fixed length
        password = hashlib.sha256(password_bytes).hexdigest()
    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Apply the same transformation as in hashing
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        plain_password = hashlib.sha256(password_bytes).hexdigest()
    
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt







def verify_token(token: str, token_type: str = "access"):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type_check: str = payload.get("type")
        
        if user_id is None or token_type_check != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return uuid.UUID(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
   
    
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