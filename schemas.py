import re
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from enum import Enum
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum
from datetime import datetime, date



class Roles(str, Enum):
    HEADMASTER = 'headmaster'
    MANAGER = 'manager'
    BURSER = 'burser'
    TEACHER = 'teacher'
    LIBRARIAN = 'librarian'
    PARENT = 'parent'
    STUDENT = 'student'

class Departments(str, Enum):
    SCIENCE = 'science'
    HUMANITIES = 'humanities'
    LANGUAGES = 'languages'

class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class GradeLevel(int, PyEnum):
    FORM_1 = 1
    FORM_2 = 2
    FORM_3 = 3
    FORM_4 = 4


class Address(BaseModel):
    street: Optional[str] = None
    village: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    gender: Gender
    phone: str  # Changed to str for phone numbers
    date_of_birth: Optional[date] = None  # Added for age-related features
    address: Optional[Address] = None     # Replaced village with Address
    role: Roles                          # Added role
    department: Optional[Departments] = None  # Added department


    @field_validator('phone')
    def validate_phone(cls, value: str) -> str:
        # Basic phone number validation (e.g., allows +1234567890)
        if not re.match(r'^\+?\d{9,15}$', value):
            raise ValueError('Invalid phone number format')
        return value




class CreateUser(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(value.encode("utf-8")) > 72:  # check byte length, not characters
            raise ValueError('Password cannot exceed 72 bytes')
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


    


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    gender: Gender
    phone: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None  # Changed to str to match database storage
    role: Roles
    department: Optional[Departments] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_seen_at: Optional[datetime] = None  # Made optional since it can be None

    model_config = ConfigDict(from_attributes=True)



class SubjectBase(BaseModel):
    name: str
    enrollment: int

class SubjectResponse(BaseModel):
    id: int
    name: str
    enrollment: int
    

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    username_or_email: str
    password: str



class DepartmentInfo(BaseModel):
    """Department information with head of department."""
    department: str
    head_of_department: Optional[str] = None  # Full name of HOD
    head_of_department_id: Optional[int] = None
    total_teachers: int
    total_students: int

class PerformanceTrend(BaseModel):
    """Performance trend data."""
    period: str  # e.g., "2024-Q1", "Jan 2024"
    average_score: float
    total_students: int
    pass_rate: float  # Percentage

class DashboardStats(BaseModel):
    """Main dashboard statistics."""
    total_students: int
    total_teachers: int
    total_departments: int
    total_parents: int
    active_users: int
    inactive_users: int

class HeadteacherDashboard(BaseModel):
    """Complete headteacher dashboard data."""
    stats: DashboardStats
    departments: List[DepartmentInfo]
    performance_trends: List[PerformanceTrend]
    recent_registrations: int  # Students registered in last 30 days
    teacher_student_ratio: str  # e.g., "1:25"

class TeacherStats(BaseModel):
    """Individual teacher statistics."""
    teacher_id: int
    teacher_name: str
    department: Optional[str]
    total_classes: int
    total_students: int
    average_performance: Optional[float] = None

class StudentStats(BaseModel):
    """Individual student statistics."""
    student_id: int
    student_name: str
    grade_level: Optional[int]
    total_subjects: int
    average_score: Optional[float] = None
    attendance_rate: Optional[float] = None
