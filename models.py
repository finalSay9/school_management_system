import re
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum
from datetime import datetime, date




class Roles(str, PyEnum):
    HEADMASTER = 'headmaster'
    MANAGER = 'manager'
    BURSER = 'burser'
    TEACHER = 'teacher'
    LIBRARIAN = 'librarian'
    PARENT = 'parent'
    STUDENT = 'student'

class Departments(str, PyEnum):
    SCIENCE = 'science'
    HUMANITIES = 'humanities'
    LANGUAGES = 'languages'

class Gender(str, PyEnum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class GradeLevel(int, PyEnum):
    FORM_1 = 1
    FORM_2 = 2
    FORM_3 = 3
    FORM_4 = 4




# SQLAlchemy Models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    gender = Column(SQLEnum(Gender), nullable=False, index=True)
    phone = Column(String(15), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    dob = Column(Date, nullable=True, index=True)
    role = Column(SQLEnum(Roles), nullable=False, index=True)
    department = Column(SQLEnum(Departments), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(Date, default=date.today, nullable=False)
    last_seen_at = Column(Date, nullable=True)