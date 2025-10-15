from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import schemas
import models
from security import get_password_hash


router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.post('/register', response_model=schemas.UserResponse)
def createUser(
    user: schemas.CreateUser,
    db: Session = Depends(get_db)
):
    # Check if the user exists by checking the email uniqueness
    check_user = db.query(models.User).filter(models.User.email == user.email).first()
    if check_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"  # Fixed: 'detail' not 'details'
        )
    
    # Format address as a string
    address = None
    if user.address:
        address_parts = [
            user.address.street,
            user.address.village,
            user.address.city,
            user.address.postal_code,
            user.address.country
        ]
        address = ", ".join([part for part in address_parts if part])  # Filter out None values

    # Create and save the user to the database
    hashed_password = get_password_hash(user.password)
    user_db = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        dob=user.date_of_birth,
        phone=user.phone,
        address=address,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@router.get('/getUsers', response_model=List[schemas.UserResponse])
def getUsers(
    db: Session = Depends(get_db)
):
    """Get all users from the database."""
    users = db.query(models.User).all()
    return users


@router.get('/getUser/{user_id}', response_model=schemas.UserResponse)
def getUser(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a single user by ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user





@router.get("/email/{email}", response_model=Optional[schemas.UserResponse])
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Get user by email"""
    user = db.query(models.User).filter(models.User.email == email, models.User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user



    

