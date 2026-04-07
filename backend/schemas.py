from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# Auth
class RegisterRequest(BaseModel):
    reg_id: str
    name: str
    department: str
    district: str
    father_name: str
    mother_name: str
    student_email: str
    parent_email: str
    parent_phone: Optional[str] = None  # Only phone - parent receives leave request via WhatsApp
    warden_maylady_email: Optional[str] = None
    password: str


class LoginRequest(BaseModel):
    reg_id_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    reg_id: str
    name: str
    department: str
    district: str
    role: str
    student_email: str
    parent_email: str
    parent_phone: Optional[str] = None
    warden_maylady_email: Optional[str] = None

    class Config:
        from_attributes = True


# Leave Request
class LeaveRequestCreate(BaseModel):
    reason: str
    departure_datetime: datetime
    arrival_datetime: datetime
    parent_phone: Optional[str] = None

    @field_validator("departure_datetime", "arrival_datetime", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            v = v.strip()
            # Handle "15-02-2026 02:33" (dd-mm-yyyy) or "2026-02-15 02:33"
            if " " in v and "T" not in v:
                date_part, time_part = v.split(" ", 1)
                if "-" in date_part:
                    parts = date_part.split("-")
                    if len(parts[0]) == 4:  # yyyy-mm-dd
                        pass
                    else:  # dd-mm-yyyy
                        date_part = f"{parts[2]}-{parts[1]}-{parts[0]}"
                v = f"{date_part}T{time_part}"
            if "T" in v and len(v.split(":")) == 2:
                v = v + ":00"
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class LeaveRequestResponse(BaseModel):
    id: int
    student_id: int
    reason: str
    departure_datetime: datetime
    arrival_datetime: datetime
    status: str
    parent_verified: Optional[bool] = False
    created_at: datetime
    student_name: Optional[str] = None
    department: Optional[str] = None
    whatsapp_sent: Optional[bool] = None  # True if parent got WhatsApp, False/None if email only
    whatsapp_error: Optional[str] = None  # User-friendly message when WhatsApp fails

    class Config:
        from_attributes = True


# Verify token
class VerifyResponse(BaseModel):
    success: bool
    message: str
    status: Optional[str] = None
