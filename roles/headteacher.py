"""
Headteacher Routes - Dashboard and management endpoints
Only accessible by users with Headteacher role
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from authentication import get_current_user
from database import get_db
import schemas
import models
from services import dashboard_service



router = APIRouter(
    prefix="/headteacher",
    tags=["Headteacher Dashboard"]
)


def require_headteacher_role(current_user: models.User = Depends(get_current_user)):
    """Dependency to check if user is a headteacher."""
    if current_user.role != schemas.Roles.HEADMASTER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only headteacher can access this resource"
        )
    return current_user


@router.get("/dashboard", response_model=schemas.HeadteacherDashboard)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """
    Get complete dashboard data for headteacher including:
    - Total students, teachers, departments
    - Department information with HODs
    - Performance trends
    - Recent registrations
    - Teacher-student ratio
    """
    return dashboard_service.get_headteacher_dashboard(db)


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get overall statistics."""
    return dashboard_service.get_dashboard_stats(db)


@router.get("/departments", response_model=List[schemas.DepartmentInfo])
def get_departments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get detailed information about all departments."""
    return dashboard_service.get_department_info(db)


@router.get("/performance-trends", response_model=List[schemas.PerformanceTrend])
def get_performance_trends(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get performance trends for the specified number of months."""
    return dashboard_service.get_performance_trends(db, months)


@router.get("/teachers", response_model=List[schemas.TeacherStats])
def get_teachers_stats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get statistics for all teachers."""
    return dashboard_service.get_teacher_statistics(db, skip, limit)


@router.get("/students", response_model=List[schemas.StudentStats])
def get_students_stats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get statistics for all students."""
    return dashboard_service.get_student_statistics(db, skip, limit)


@router.get("/recent-registrations")
def get_recent_registrations(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get number of students registered in the last N days."""
    count = dashboard_service.get_recent_registrations(db, days)
    return {
        "days": days,
        "total_registrations": count,
        "message": f"{count} students registered in the last {days} days"
    }


@router.get("/teacher-student-ratio")
def get_ratio(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_headteacher_role)
):
    """Get teacher to student ratio."""
    ratio = dashboard_service.calculate_teacher_student_ratio(db)
    return {
        "ratio": ratio,
        "message": f"Current teacher-student ratio is {ratio}"
    }