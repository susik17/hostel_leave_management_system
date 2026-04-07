"""Run once to create tables and optional default warden. Usage: python init_db.py"""
from sqlalchemy import text
from database import engine, Base, SessionLocal
from models import Student
from auth import hash_password
from config import get_settings

settings = get_settings()

def init():
    Base.metadata.create_all(bind=engine)
    # Migrate: add parent_verified if missing (for existing DBs)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE leave_requests ADD COLUMN parent_verified BOOLEAN DEFAULT 0"))
            conn.commit()
    except Exception:
        pass
    # Migrate: add warden_token columns for email action links
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE leave_requests ADD COLUMN warden_token VARCHAR(100)"))
            conn.commit()
    except Exception:
        pass
    try:
        with engine.connect() as conn:
            if "postgresql" in str(engine.url):
                conn.execute(text("ALTER TABLE leave_requests ADD COLUMN warden_token_expiry TIMESTAMP"))
            else:
                conn.execute(text("ALTER TABLE leave_requests ADD COLUMN warden_token_expiry DATETIME"))
            conn.commit()
    except Exception:
        pass
    for col, col_type in [
        ("parent_phone", "VARCHAR(20)"),
        ("warden_maylady_email", "VARCHAR(255)"),
    ]:
        try:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE students ADD COLUMN {col} {col_type}"))
                conn.commit()
        except Exception:
            pass
    # Migrate: allow same email for multiple students (drop unique index)
    if "postgresql" in str(engine.url):
        try:
            with engine.connect() as conn:
                conn.execute(text("DROP INDEX IF EXISTS ix_students_student_email"))
                conn.commit()
        except Exception:
            pass
    db = SessionLocal()
    try:
        if not db.query(Student).filter(Student.role == "warden").first():
            warden = Student(
                reg_id="warden001",
                name="Hostel Warden",
                department="Admin",
                district="Admin",
                father_name="-",
                mother_name="-",
                student_email=settings.warden_email,
                parent_email="-",
                password_hash=hash_password("warden123"),
                role="warden",
            )
            db.add(warden)
            db.commit()
            print("Default warden created: warden001 / warden123")
        else:
            print("Warden already exists")
    finally:
        db.close()

if __name__ == "__main__":
    init()
