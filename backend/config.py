from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Load .env from backend directory (works even when uvicorn runs from project root)
_env_path = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hostel_leave.db"
    jwt_secret: str = "change-me-in-production-use-secrets-token-hex"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    # Single account (legacy fallback)
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@hostelleave.com"
    # Three accounts: parent, warden, student
    smtp_parent_email: str = ""
    smtp_parent_password: str = ""
    smtp_warden_email: str = ""
    smtp_warden_password: str = ""
    smtp_student_email: str = ""
    smtp_student_password: str = ""
    frontend_url: str = "http://localhost:5175"
    backend_url: str = ""  # Public backend URL for short links (e.g. https://api.example.com). If empty, uses frontend_url for links.
    warden_email: str = "genzovasoftwaresolutions@gmail.com"
    token_expiry_hours: int = 24
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    twilio_whatsapp_from: str = ""
    twilio_leave_content_sid: str = ""  # Content Template SID for interactive Approve/Reject buttons
    whatsapp_reply_mode: bool = True  # True = parent replies "accept"/"reject" in WhatsApp (no links)
    # Meta WhatsApp Cloud API - 1,000 free conversations/month
    meta_whatsapp_phone_id: str = ""  # Phone Number ID from Meta app
    meta_whatsapp_token: str = ""  # Permanent access token
    meta_whatsapp_leave_template: str = ""  # Template name for leave request (create in Meta)
    meta_whatsapp_approved_template: str = ""  # Template name for leave approved
    meta_whatsapp_lang: str = "en"
    meta_webhook_verify_token: str = "hostel-leave-verify"  # For webhook GET verification

    class Config:
        env_file = str(_env_path) if _env_path.exists() else ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()
