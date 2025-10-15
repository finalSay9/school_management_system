"""
HR Routes - Human Resources management endpoints
Only accessible by users with HR/Manager roles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from authentication import get_current_user
from database import get_db
import schemas
import models
from services import user_service



router = APIRouter(
    prefix="/hr",
    tags=["HR Management"]
)


def require_hr_role(current_user: models.User = Depends(get_current_user)):
    """Dependency to check if user has HR privileges."""
    allowed_roles = [schemas.Roles.HEADMASTER, schemas.Roles.MANAGER]
    
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )
    return current_user


@router.post("/create-teacher", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_data: schemas.CreateUser,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """
    Create a new teacher account.
    Only accessible by Headmaster and Manager.
    """
    # Ensure the role is set to teacher
    if teacher_data.role != schemas.Roles.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for creating teacher accounts"
        )
    
    # Reuse the user creation logic
    new_teacher = user_service.create_user(db, teacher_data, created_by=current_user.id)
    
    return new_teacher


@router.post("/create-staff", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: schemas.CreateUser,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """
    Create a new staff member (Librarian, Bursar, etc.).
    Only accessible by Headmaster and Manager.
    """
    allowed_staff_roles = [
        schemas.Roles.LIBRARIAN,
        schemas.Roles.BURSER,
        schemas.Roles.TEACHER
    ]
    
    if staff_data.role not in allowed_staff_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid staff role. Allowed roles: {', '.join([r.value for r in allowed_staff_roles])}"
        )
    
    # Reuse the user creation logic
    new_staff = user_service.create_user(db, staff_data, created_by=current_user.id)
    
    return new_staff


@router.get("/teachers", response_model=List[schemas.UserResponse])
def get_all_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """Get all teachers."""
    return user_service.get_users_by_role(db, schemas.Roles.TEACHER, skip, limit)


@router.get("/staff", response_model=List[schemas.UserResponse])
def get_all_staff(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """Get all staff members."""
    staff_roles = [schemas.Roles.LIBRARIAN, schemas.Roles.BURSER, schemas.Roles.TEACHER]
    
    staff = db.query(models.User).filter(
        models.User.role.in_(staff_roles)
    ).offset(skip).limit(limit).all()
    
    return staff


@router.patch("/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """Deactivate a user account."""
    user = user_service.deactivate_user(db, user_id)
    return {"message": f"User {user.email} has been deactivated"}


@router.patch("/activate/{user_id}")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """Activate a user account."""
    user = user_service.activate_user(db, user_id)
    return {"message": f"User {user.email} has been activated"}


@router.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr_role)
):
    """Get detailed information about a specific user."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user