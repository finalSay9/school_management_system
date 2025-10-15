from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import schemas
import models
from security import get_password_hash
from services import user_service  # Import the service


router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.post('/register', response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def createUser(
    user: schemas.CreateUser,
    db: Session = Depends(get_db)
):
    """Public user registration endpoint."""
    return user_service.create_user(db, user)


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