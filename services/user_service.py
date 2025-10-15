"""
User Service - Shared business logic for user operations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
import models
import schemas
from security import get_password_hash


def create_user(
    db: Session,
    user_data: schemas.CreateUser,
    created_by: Optional[int] = None
) -> models.User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        user_data: User data from request
        created_by: ID of user who created this user (for HR tracking)
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Format address
    address = None
    if user_data.address:
        address_parts = [
            user_data.address.street,
            user_data.address.village,
            user_data.address.city,
            user_data.address.postal_code,
            user_data.address.country
        ]
        address = ", ".join([part for part in address_parts if part])
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    new_user = models.User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        gender=user_data.gender,
        dob=user_data.date_of_birth,
        phone=user_data.phone,
        address=address,
        role=user_data.role,
        department=user_data.department,
        hashed_password=hashed_password
    )
    
    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_by_role(db: Session, role: schemas.Roles, skip: int = 0, limit: int = 100):
    """Get users by role with pagination."""
    return db.query(models.User).filter(
        models.User.role == role
    ).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_data: dict) -> models.User:
    """Update user information."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    for key, value in user_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> models.User:
    """Deactivate a user account."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def activate_user(db: Session, user_id: int) -> models.User:
    """Activate a user account."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user