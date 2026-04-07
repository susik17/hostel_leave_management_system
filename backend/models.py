from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    reg_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    father_name = Column(String(100), nullable=False)
    mother_name = Column(String(100), nullable=False)
    student_email = Column(String(255), nullable=False, index=True)
    parent_email = Column(String(255), nullable=False)
    parent_phone = Column(String(20), nullable=True)  # Only phone in system - parent receives WhatsApp
    warden_maylady_email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    created_at = Column(DateTime, default=datetime.utcnow)

    leave_requests = relationship("LeaveRequest", back_populates="student")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    reason = Column(Text, nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)
    status = Column(String(30), default="PARENT_PENDING")
    parent_verified = Column(Boolean, default=False)
    approval_token = Column(String(100), unique=True, index=True)
    token_expiry = Column(DateTime, nullable=True)
    token_used = Column(Boolean, default=False)
    warden_token = Column(String(100), unique=True, index=True, nullable=True)
    warden_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="leave_requests")
