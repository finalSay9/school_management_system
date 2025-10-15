"""
Dashboard Service - Business logic for dashboard data
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import models
import schemas


def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    """Get overall dashboard statistics."""
    
    # Count users by role
    total_students = db.query(models.User).filter(
        models.User.role == schemas.Roles.STUDENT
    ).count()
    
    total_teachers = db.query(models.User).filter(
        models.User.role == schemas.Roles.TEACHER
    ).count()
    
    total_parents = db.query(models.User).filter(
        models.User.role == schemas.Roles.PARENT
    ).count()
    
    # Count unique departments
    total_departments = db.query(models.User.department).filter(
        models.User.department.isnot(None)
    ).distinct().count()
    
    # Active vs inactive users
    active_users = db.query(models.User).filter(
        models.User.is_active == True
    ).count()
    
    inactive_users = db.query(models.User).filter(
        models.User.is_active == False
    ).count()
    
    return schemas.DashboardStats(
        total_students=total_students,
        total_teachers=total_teachers,
        total_departments=total_departments,
        total_parents=total_parents,
        active_users=active_users,
        inactive_users=inactive_users
    )


def get_department_info(db: Session) -> List[schemas.DepartmentInfo]:
    """Get information about each department including HOD."""
    
    departments_data = []
    
    # Get all unique departments
    departments = db.query(models.User.department).filter(
        models.User.department.isnot(None)
    ).distinct().all()
    
    for (dept,) in departments:
        # Count teachers in this department
        total_teachers = db.query(models.User).filter(
            models.User.department == dept,
            models.User.role == schemas.Roles.TEACHER
        ).count()
        
        # Count students in this department (if applicable)
        total_students = db.query(models.User).filter(
            models.User.department == dept,
            models.User.role == schemas.Roles.STUDENT
        ).count()
        
        # Find HOD - for now, we'll take the most senior teacher (earliest created_at)
        # You might want to add a specific 'is_hod' field to User model later
        hod = db.query(models.User).filter(
            models.User.department == dept,
            models.User.role == schemas.Roles.TEACHER
        ).order_by(models.User.created_at.asc()).first()
        
        hod_name = None
        hod_id = None
        if hod:
            hod_name = f"{hod.first_name} {hod.last_name}"
            hod_id = hod.id
        
        departments_data.append(schemas.DepartmentInfo(
            department=dept.value if hasattr(dept, 'value') else dept,
            head_of_department=hod_name,
            head_of_department_id=hod_id,
            total_teachers=total_teachers,
            total_students=total_students
        ))
    
    return departments_data


def get_performance_trends(db: Session, months: int = 6) -> List[schemas.PerformanceTrend]:
    """
    Get performance trends for the last N months.
    
    Note: This is a placeholder. You'll need to implement this based on your
    grades/results table structure. For now, it returns sample data.
    """
    
    # TODO: Replace this with actual performance data from your grades table
    # Example query structure:
    # trends = db.query(
    #     func.date_trunc('month', models.Grade.date).label('period'),
    #     func.avg(models.Grade.score).label('average_score'),
    #     func.count(models.Grade.student_id.distinct()).label('total_students')
    # ).group_by('period').order_by(desc('period')).limit(months).all()
    
    trends = []
    today = datetime.now()
    
    for i in range(months):
        month_date = today - timedelta(days=30 * i)
        period = month_date.strftime("%b %Y")
        
        # Placeholder data - replace with actual grades query
        trends.append(schemas.PerformanceTrend(
            period=period,
            average_score=0.0,  # Replace with actual average
            total_students=0,   # Replace with actual count
            pass_rate=0.0       # Replace with actual pass rate
        ))
    
    return trends


def get_recent_registrations(db: Session, days: int = 30) -> int:
    """Get number of students registered in the last N days."""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    recent_students = db.query(models.User).filter(
        models.User.role == schemas.Roles.STUDENT,
        models.User.created_at >= cutoff_date
    ).count()
    
    return recent_students


def calculate_teacher_student_ratio(db: Session) -> str:
    """Calculate teacher to student ratio."""
    
    total_teachers = db.query(models.User).filter(
        models.User.role == schemas.Roles.TEACHER,
        models.User.is_active == True
    ).count()
    
    total_students = db.query(models.User).filter(
        models.User.role == schemas.Roles.STUDENT,
        models.User.is_active == True
    ).count()
    
    if total_teachers == 0:
        return "N/A"
    
    ratio = total_students / total_teachers
    return f"1:{ratio:.0f}"


def get_headteacher_dashboard(db: Session) -> schemas.HeadteacherDashboard:
    """Get complete dashboard data for headteacher."""
    
    stats = get_dashboard_stats(db)
    departments = get_department_info(db)
    performance_trends = get_performance_trends(db)
    recent_registrations = get_recent_registrations(db)
    teacher_student_ratio = calculate_teacher_student_ratio(db)
    
    return schemas.HeadteacherDashboard(
        stats=stats,
        departments=departments,
        performance_trends=performance_trends,
        recent_registrations=recent_registrations,
        teacher_student_ratio=teacher_student_ratio
    )


def get_teacher_statistics(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.TeacherStats]:
    """Get statistics for all teachers."""
    
    teachers = db.query(models.User).filter(
        models.User.role == schemas.Roles.TEACHER
    ).offset(skip).limit(limit).all()
    
    teacher_stats = []
    for teacher in teachers:
        teacher_name = f"{teacher.first_name} {teacher.last_name}"
        
        # TODO: Add actual class and student counts from your classes table
        # total_classes = db.query(models.Class).filter(
        #     models.Class.teacher_id == teacher.id
        # ).count()
        
        teacher_stats.append(schemas.TeacherStats(
            teacher_id=teacher.id,
            teacher_name=teacher_name,
            department=teacher.department.value if teacher.department else None,
            total_classes=0,  # Replace with actual count
            total_students=0,  # Replace with actual count
            average_performance=None  # Replace with actual performance data
        ))
    
    return teacher_stats


def get_student_statistics(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.StudentStats]:
    """Get statistics for all students."""
    
    students = db.query(models.User).filter(
        models.User.role == schemas.Roles.STUDENT
    ).offset(skip).limit(limit).all()
    
    student_stats = []
    for student in students:
        student_name = f"{student.first_name} {student.last_name}"
        
        # TODO: Add actual subject count and performance from your enrollment/grades tables
        
        student_stats.append(schemas.StudentStats(
            student_id=student.id,
            student_name=student_name,
            grade_level=None,  # Add grade_level field to User model if needed
            total_subjects=0,  # Replace with actual count
            average_score=None,  # Replace with actual average
            attendance_rate=None  # Replace with actual attendance data
        ))
    
    return student_stats