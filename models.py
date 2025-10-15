import re
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from sqlalchemy import Column, DateTime, Float, Integer, String, Date, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum
from datetime import datetime, date
import enum


# Enums
class RoleEnum(str, enum.Enum):
    HEADMASTER = 'headmaster'
    MANAGER = 'manager'
    BURSER = 'burser'
    TEACHER = 'teacher'
    LIBRARIAN = 'librarian'
    PARENT = 'parent'
    STUDENT = 'student'


class DepartmentEnum(str, enum.Enum):
    SCIENCE = 'science'
    HUMANITIES = 'humanities'
    LANGUAGES = 'languages'


class GenderEnum(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class GradeLevelEnum(int, enum.Enum):
    FORM_1 = 1
    FORM_2 = 2
    FORM_3 = 3
    FORM_4 = 4


class TermEnum(str, enum.Enum):
    TERM_1 = 'term_1'
    TERM_2 = 'term_2'
    TERM_3 = 'term_3'


class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = 'present'
    ABSENT = 'absent'
    LATE = 'late'
    EXCUSED = 'excused'


# ==================== USER MODEL ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    phone = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    
    # Role and Department
    role = Column(SQLEnum(RoleEnum), nullable=False, index=True)
    department = Column(SQLEnum(DepartmentEnum), nullable=True, index=True)
    is_hod = Column(Boolean, default=False)  # Head of Department flag
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True)
    
    # Student specific fields
    grade_level = Column(Integer, nullable=True)  # Form 1-4
    admission_number = Column(String, unique=True, nullable=True, index=True)
    admission_date = Column(Date, nullable=True)
    
    # Teacher specific fields
    employee_number = Column(String, unique=True, nullable=True, index=True)
    hire_date = Column(Date, nullable=True)
    qualification = Column(String, nullable=True)
    
    # Relationships
    taught_classes = relationship("Class", back_populates="teacher", foreign_keys="Class.teacher_id")
    enrolled_classes = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    parent_relationships = relationship("ParentStudent", foreign_keys="ParentStudent.student_id", back_populates="student")
    children_relationships = relationship("ParentStudent", foreign_keys="ParentStudent.parent_id", back_populates="parent")


# ==================== SUBJECT MODEL ====================
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    code = Column(String, unique=True, nullable=False)  # e.g., "MTH101"
    description = Column(Text, nullable=True)
    department = Column(SQLEnum(DepartmentEnum), nullable=True)
    credit_hours = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classes = relationship("Class", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")


# ==================== CLASS MODEL ====================
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Form 1A - Mathematics"
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    grade_level = Column(Integer, nullable=False)  # Form 1-4
    academic_year = Column(String, nullable=False)  # e.g., "2024/2025"
    term = Column(SQLEnum(TermEnum), nullable=False)
    
    room_number = Column(String, nullable=True)
    schedule = Column(String, nullable=True)  # e.g., "Mon 8:00-9:00, Wed 10:00-11:00"
    max_students = Column(Integer, default=40)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="classes")
    teacher = relationship("User", back_populates="taught_classes", foreign_keys=[teacher_id])
    enrollments = relationship("Enrollment", back_populates="class_obj")
    grades = relationship("Grade", back_populates="class_obj")
    attendance = relationship("Attendance", back_populates="class_obj")


# ==================== ENROLLMENT MODEL ====================
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    enrollment_date = Column(Date, default=datetime.utcnow)
    status = Column(String, default="active")  # active, dropped, completed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="enrolled_classes")
    class_obj = relationship("Class", back_populates="enrollments")


# ==================== GRADE MODEL ====================
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # Grade details
    assessment_type = Column(String, nullable=False)  # "exam", "assignment", "quiz", "midterm", "final"
    score = Column(Float, nullable=False)  # 0-100
    max_score = Column(Float, default=100.0)
    percentage = Column(Float, nullable=True)  # Calculated: (score/max_score) * 100
    grade_letter = Column(String, nullable=True)  # A, B, C, D, F
    
    # Assessment details
    assessment_name = Column(String, nullable=False)  # e.g., "Midterm Exam", "Assignment 1"
    assessment_date = Column(Date, nullable=False)
    academic_year = Column(String, nullable=False)
    term = Column(SQLEnum(TermEnum), nullable=False)
    
    # Additional info
    remarks = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    class_obj = relationship("Class", back_populates="grades")


# ==================== ATTENDANCE MODEL ====================
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(AttendanceStatusEnum), nullable=False)
    remarks = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="attendance_records")
    class_obj = relationship("Class", back_populates="attendance")


# ==================== PARENT-STUDENT RELATIONSHIP ====================
class ParentStudent(Base):
    __tablename__ = "parent_student"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    relationship_type = Column(String, nullable=False)  # "father", "mother", "guardian"
    is_primary_contact = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("User", foreign_keys=[parent_id], back_populates="children_relationships")
    student = relationship("User", foreign_keys=[student_id], back_populates="parent_relationships")


# ==================== ANNOUNCEMENT MODEL ====================
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    target_audience = Column(String, nullable=False)  # "all", "students", "teachers", "parents", "specific_grade"
    target_grade_level = Column(Integer, nullable=True)
    
    priority = Column(String, default="normal")  # "low", "normal", "high", "urgent"
    is_published = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    publish_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)


# ==================== FEE MODEL ====================
class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    academic_year = Column(String, nullable=False)
    term = Column(SQLEnum(TermEnum), nullable=False)
    
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    balance = Column(Float, nullable=False)
    
    due_date = Column(Date, nullable=False)
    payment_status = Column(String, default="pending")  # "pending", "partial", "paid", "overdue"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== PAYMENT MODEL ====================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    fee_id = Column(Integer, ForeignKey("fees.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # "cash", "bank_transfer", "mobile_money"
    transaction_reference = Column(String, unique=True, nullable=True)
    
    payment_date = Column(Date, nullable=False)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    remarks = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)