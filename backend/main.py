from datetime import datetime, timedelta, date
import asyncio
import secrets
from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db, SessionLocal, engine, Base
from models import Student, LeaveRequest
from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    VerifyResponse,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_warden,
)
from config import get_settings
from email_service import (
    send_email,
    send_parent_verification_email,
    send_parent_approved_to_warden,
    send_parent_approved_to_student,
    send_parent_rejected_emails,
    send_leave_approved_emails,
    send_leave_rejected_emails,
)

Base.metadata.create_all(bind=engine)
settings = get_settings()
if settings.twilio_account_sid and settings.twilio_whatsapp_from:
    print(f"[Startup] Twilio WhatsApp configured: from={settings.twilio_whatsapp_from}")
else:
    print(f"[Startup] Twilio NOT configured - WhatsApp disabled")

if settings.smtp_warden_email and settings.smtp_warden_password:
    print(f"[Startup] Warden SMTP configured: sends to {settings.warden_email}")
else:
    print(f"[Startup] Warden SMTP NOT configured - set SMTP_WARDEN_EMAIL, SMTP_WARDEN_PASSWORD in .env")

app = FastAPI(title="Hostel Leave Approval API")


@app.exception_handler(Exception)
async def catch_all(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    import traceback
    import sys
    tb = traceback.format_exc()
    print(tb, file=sys.stderr, flush=True)
    # Include last traceback lines in response for debugging (helpful for 500 errors)
    lines = [ln.strip() for ln in tb.strip().split("\n") if ln.strip()][-5:]
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": lines})


# Allow all localhost origins for dev (frontend may run on 5175-5190)
_app_origins = [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176",
    "http://localhost:5177", "http://localhost:5178", "http://localhost:5179", "http://localhost:5180",
    "http://localhost:5181", "http://localhost:5182", "http://localhost:5183", "http://localhost:5184",
    "http://localhost:5185", "http://localhost:3000",
    "http://127.0.0.1:5173", "http://127.0.0.1:5175", "http://127.0.0.1:5176", "http://127.0.0.1:5184",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_app_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/go/a/{token}")
def redirect_approve(token: str):
    """Short link for parent Approve - redirects to frontend parent-action."""
    return RedirectResponse(url=f"{settings.frontend_url}/parent-action?token={token}&type=approve", status_code=302)


@app.get("/go/r/{token}")
def redirect_reject(token: str):
    """Short link for parent Reject - redirects to frontend parent-action."""
    return RedirectResponse(url=f"{settings.frontend_url}/parent-action?token={token}&type=reject", status_code=302)


def user_to_response(user: Student) -> UserResponse:
    return UserResponse(
        id=user.id,
        reg_id=user.reg_id,
        name=user.name,
        department=user.department,
        district=user.district,
        role=user.role,
        student_email=user.student_email,
        parent_email=user.parent_email,
        parent_phone=getattr(user, "parent_phone", None),
        warden_maylady_email=getattr(user, "warden_maylady_email", None),
    )


@app.post("/api/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Student).filter(Student.reg_id == data.reg_id).first():
        raise HTTPException(400, "Reg ID already registered")
    user = Student(
        reg_id=data.reg_id,
        name=data.name,
        department=data.department,
        district=data.district,
        father_name=data.father_name,
        mother_name=data.mother_name,
        student_email=data.student_email,
        parent_email=data.parent_email,
        parent_phone=data.parent_phone or None,
        warden_maylady_email=data.warden_maylady_email or None,
        password_hash=hash_password(data.password),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user_to_response(user))


@app.post("/api/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Student).filter(
        or_(
            Student.reg_id == data.reg_id_or_email,
            Student.student_email == data.reg_id_or_email,
        )
    ).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user_to_response(user))


@app.get("/api/me", response_model=UserResponse)
def me(user: Student = Depends(get_current_user)):
    return user_to_response(user)


@app.post("/api/leave", response_model=LeaveRequestResponse)
async def create_leave(
    data: LeaveRequestCreate,
    background_tasks: BackgroundTasks,
    user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.arrival_datetime <= data.departure_datetime:
        raise HTTPException(400, "Arrival must be after departure")
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=settings.token_expiry_hours)
    leave = LeaveRequest(
        student_id=user.id,
        reason=data.reason,
        departure_datetime=data.departure_datetime,
        arrival_datetime=data.arrival_datetime,
        status="PARENT_PENDING",
        approval_token=token,
        token_expiry=expiry,
        token_used=False,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    parent_email = user.parent_email
    parent_phone = (data.parent_phone or getattr(user, "parent_phone", None) or "").strip()
    print(f"[Leave] data.parent_phone={repr(data.parent_phone)} -> parent_phone={repr(parent_phone)}")
    student_name = user.name
    department = user.department
    reason = data.reason
    departure = data.departure_datetime
    arrival = data.arrival_datetime
    base = (settings.backend_url or settings.frontend_url).rstrip("/")
    approve_url = f"{base}/go/a/{token}" if settings.backend_url else f"{settings.frontend_url}/parent-action?token={token}&type=approve"
    reject_url = f"{base}/go/r/{token}" if settings.backend_url else f"{settings.frontend_url}/parent-action?token={token}&type=reject"
    dep_str = departure.strftime("%d %b %Y, %I:%M %p") if hasattr(departure, "strftime") else str(departure)
    arr_str = arrival.strftime("%d %b %Y, %I:%M %p") if hasattr(arrival, "strftime") else str(arrival)

    whatsapp_sent = False
    whatsapp_error = None
    if parent_phone:
        try:
            if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from:
                from whatsapp_service import send_leave_request_to_parent as send_wa
                await send_wa(parent_phone, student_name, department, reason, dep_str, arr_str, approve_url, reject_url)
                whatsapp_sent = True
                print(f"[Leave] WhatsApp sent to {parent_phone}")
            elif settings.meta_whatsapp_phone_id and settings.meta_whatsapp_token:
                from meta_whatsapp_service import send_leave_request_to_parent as send_wa
                await send_wa(parent_phone, student_name, department, reason, dep_str, arr_str, approve_url, reject_url)
                whatsapp_sent = True
            else:
                await send_parent_verification_email(parent_email, student_name, department, reason, departure, arrival, token)
        except Exception as ex:
            import traceback
            print(f"[WhatsApp] FAILED: {ex}")
            traceback.print_exc()
            whatsapp_error = str(ex)  # User-friendly message for sandbox issues
            try:
                await send_parent_verification_email(parent_email, student_name, department, reason, departure, arrival, token)
                print(f"[Leave] Fallback: Email sent to parent")
            except Exception as e2:
                print(f"[SMTP] Fallback email failed: {e2}")
    else:
        try:
            await send_parent_verification_email(parent_email, student_name, department, reason, departure, arrival, token)
        except Exception as ex:
            import traceback
            print(f"[SMTP] Parent email failed: {ex}")
            traceback.print_exc()

    return LeaveRequestResponse(
        id=leave.id,
        student_id=leave.student_id,
        reason=leave.reason,
        departure_datetime=leave.departure_datetime,
        arrival_datetime=leave.arrival_datetime,
        status=leave.status,
        parent_verified=leave.parent_verified,
        created_at=leave.created_at,
        student_name=user.name,
        department=user.department,
        whatsapp_sent=whatsapp_sent,
        whatsapp_error=whatsapp_error,
    )


@app.get("/api/leave-preview")
def leave_preview(token: str, db: Session = Depends(get_db)):
    """Get leave details by token (read-only, for single-link choice page). Does not consume token."""
    leave = db.query(LeaveRequest).filter(LeaveRequest.approval_token == token).first()
    if not leave:
        return {"valid": False, "message": "Invalid link"}
    if leave.token_used:
        return {"valid": False, "message": "Already used"}
    if datetime.utcnow() > leave.token_expiry:
        return {"valid": False, "message": "Link expired"}
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    dep = leave.departure_datetime
    arr = leave.arrival_datetime
    return {
        "valid": True,
        "student_name": student.name,
        "department": student.department,
        "reason": leave.reason,
        "departure": dep.strftime("%d %b %Y, %I:%M %p") if hasattr(dep, "strftime") else str(dep),
        "arrival": arr.strftime("%d %b %Y, %I:%M %p") if hasattr(arr, "strftime") else str(arr),
    }


@app.get("/api/parent-action")
async def parent_action(
    token: str,
    type: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Parent clicks Confirm or Reject link. type=approve or type=reject."""
    if type not in ("approve", "reject"):
        return VerifyResponse(success=False, message="Invalid action")
    leave = db.query(LeaveRequest).filter(LeaveRequest.approval_token == token).first()
    if not leave:
        return VerifyResponse(success=False, message="Invalid link")
    if leave.token_used:
        return VerifyResponse(success=False, message="Already used")
    if datetime.utcnow() > leave.token_expiry:
        return VerifyResponse(success=False, message="Link expired")
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    leave.token_used = True
    if type == "approve":
        leave.status = "WARDEN_PENDING"
        leave.parent_verified = True
        leave.warden_token = secrets.token_urlsafe(32)
        leave.warden_token_expiry = datetime.utcnow() + timedelta(hours=settings.token_expiry_hours)
    else:
        leave.status = "REJECTED_BY_PARENT"
    db.commit()

    if type == "approve":
        warden_email = settings.warden_email
        name, dept = student.name, student.department
        reason = leave.reason
        dep, arr = leave.departure_datetime, leave.arrival_datetime
        warden_token = leave.warden_token
        student_email = student.student_email

        async def _send_after_parent_approve():
            try:
                await send_parent_approved_to_warden(
                    warden_email, name, dept, reason, dep, arr, warden_token
                )
                print(f"[Parent-Action] Warden email sent to {warden_email}")
            except Exception as ex:
                import traceback
                print(f"[Parent-Action SMTP] Warden email FAILED to {warden_email}: {ex}")
                traceback.print_exc()
            try:
                await send_parent_approved_to_student(student_email, name, dep)
            except Exception as ex:
                import traceback
                print(f"[SMTP] Student notification failed: {ex}")
                traceback.print_exc()
        background_tasks.add_task(_send_after_parent_approve)
        return VerifyResponse(
            success=True,
            message="Leave confirmed. Warden will receive email and approve shortly.",
            status="WARDEN_PENDING",
        )
    else:
        student_email = student.student_email
        warden_email = settings.warden_email

        async def _send_rejected():
            try:
                await send_parent_rejected_emails(student_email, warden_email)
            except Exception as ex:
                import traceback
                print(f"[SMTP] Parent-rejected emails failed: {ex}")
                traceback.print_exc()
        background_tasks.add_task(_send_rejected)
        return VerifyResponse(success=False, message="Leave rejected by parent. Request closed.", status="REJECTED_BY_PARENT")


@app.get("/api/verify")
async def verify_legacy(
    token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Legacy: old /verify?token=x - treat as parent approve."""
    leave = db.query(LeaveRequest).filter(LeaveRequest.approval_token == token).first()
    if not leave:
        return VerifyResponse(success=False, message="Invalid link")
    if leave.token_used:
        return VerifyResponse(success=False, message="Already used")
    if datetime.utcnow() > leave.token_expiry:
        return VerifyResponse(success=False, message="Link expired")
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    leave.token_used = True
    leave.status = "WARDEN_PENDING"
    leave.parent_verified = True
    leave.warden_token = secrets.token_urlsafe(32)
    leave.warden_token_expiry = datetime.utcnow() + timedelta(hours=settings.token_expiry_hours)
    db.commit()
    warden_email = settings.warden_email
    name, dept = student.name, student.department
    reason = leave.reason
    dep, arr = leave.departure_datetime, leave.arrival_datetime
    warden_token = leave.warden_token
    student_email = student.student_email

    async def _send_after_verify():
        try:
            await send_parent_approved_to_warden(
                warden_email, name, dept, reason, dep, arr, warden_token
            )
            print(f"[Verify] Warden email sent to {warden_email}")
        except Exception as ex:
            import traceback
            print(f"[Verify SMTP] Warden email FAILED to {warden_email}: {ex}")
            traceback.print_exc()
        try:
            await send_parent_approved_to_student(student_email, name, dep)
        except Exception as ex:
            import traceback
            print(f"[Verify SMTP] Student notification failed: {ex}")
            traceback.print_exc()
    background_tasks.add_task(_send_after_verify)
    return VerifyResponse(success=True, message="Verified. Warden will receive email and approve shortly.", status="WARDEN_PENDING")


@app.post("/api/leave/{leave_id}/approve")
async def warden_approve(
    leave_id: int,
    background_tasks: BackgroundTasks,
    user: Student = Depends(get_current_warden),
    db: Session = Depends(get_db),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "Leave not found")
    if leave.status not in ("WARDEN_PENDING", "Pending"):
        raise HTTPException(400, f"Cannot approve: status is {leave.status}")
    if not leave.parent_verified:
        raise HTTPException(400, "Parent must verify first")
    leave.status = "Approved"
    db.commit()
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    student_email = student.student_email
    parent_email = student.parent_email
    student_name = student.name
    departure = leave.departure_datetime

    async def _send_approved():
        try:
            await send_leave_approved_emails(student_email, parent_email, student_name, departure)
        except Exception as ex:
            import traceback
            print(f"[SMTP] Approved emails failed: {ex}")
            traceback.print_exc()
    background_tasks.add_task(_send_approved)
    return {"success": True, "status": "Approved"}


@app.post("/api/leave/{leave_id}/reject")
async def warden_reject(
    leave_id: int,
    background_tasks: BackgroundTasks,
    user: Student = Depends(get_current_warden),
    db: Session = Depends(get_db),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "Leave not found")
    if leave.status not in ("WARDEN_PENDING", "Pending"):
        raise HTTPException(400, f"Cannot reject: status is {leave.status}")
    leave.status = "REJECTED_BY_WARDEN"
    db.commit()
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    student_email = student.student_email
    parent_email = student.parent_email
    student_name = student.name

    async def _send_rejected():
        try:
            await send_leave_rejected_emails(student_email, parent_email, student_name)
        except Exception as ex:
            import traceback
            print(f"[SMTP] Rejected emails failed: {ex}")
            traceback.print_exc()
    background_tasks.add_task(_send_rejected)
    return {"success": True, "status": "REJECTED_BY_WARDEN"}


@app.get("/api/warden-action")
async def warden_action(
    token: str,
    type: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Warden clicks Leave Approved or Leave Rejected link in email. Updates status and notifies student+parent."""
    if type not in ("approve", "reject"):
        return VerifyResponse(success=False, message="Invalid action")
    leave = db.query(LeaveRequest).filter(LeaveRequest.warden_token == token).first()
    if not leave:
        return VerifyResponse(success=False, message="Invalid or expired link")
    if leave.status not in ("WARDEN_PENDING", "Pending"):
        return VerifyResponse(success=False, message=f"Leave already {leave.status}")
    if leave.warden_token_expiry and datetime.utcnow() > leave.warden_token_expiry:
        return VerifyResponse(success=False, message="Link expired")
    student = db.query(Student).filter(Student.id == leave.student_id).first()

    if type == "approve":
        leave.status = "Approved"
        leave.warden_token = None
        db.commit()
        student_email = student.student_email
        parent_email = student.parent_email
        student_name = student.name
        departure = leave.departure_datetime

        async def _send_approved():
            try:
                await send_leave_approved_emails(
                    student_email, parent_email, student_name, departure
                )
            except Exception as ex:
                import traceback
                print(f"[SMTP] Approved emails failed: {ex}")
                traceback.print_exc()
        background_tasks.add_task(_send_approved)
        return VerifyResponse(success=True, message="Leave approved. Student and parent have been notified.", status="Approved")
    else:
        leave.status = "REJECTED_BY_WARDEN"
        leave.warden_token = None
        db.commit()
        student_email = student.student_email
        parent_email = student.parent_email
        student_name = student.name

        async def _send_rejected():
            try:
                await send_leave_rejected_emails(student_email, parent_email, student_name)
            except Exception as ex:
                import traceback
                print(f"[SMTP] Rejected emails failed: {ex}")
                traceback.print_exc()
        background_tasks.add_task(_send_rejected)
        return VerifyResponse(success=False, message="Leave rejected. Student and parent have been notified.", status="REJECTED_BY_WARDEN")


@app.get("/api/leave/my", response_model=list[LeaveRequestResponse])
def my_leave_requests(
    user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    leaves = db.query(LeaveRequest).filter(LeaveRequest.student_id == user.id).order_by(LeaveRequest.created_at.desc()).all()
    return [
        LeaveRequestResponse(
            id=l.id,
            student_id=l.student_id,
            reason=l.reason,
            departure_datetime=l.departure_datetime,
            arrival_datetime=l.arrival_datetime,
            status=l.status,
            parent_verified=l.parent_verified,
            created_at=l.created_at,
            student_name=user.name,
            department=user.department,
        )
        for l in leaves
    ]


@app.get("/api/warden/date-stats")
def warden_date_stats(
    search_date: str,
    user: Student = Depends(get_current_warden),
    db: Session = Depends(get_db),
):
    """For a given date: remaining (in hostel), away (on leave), food count = remaining."""
    try:
        search_date = search_date.strip().rstrip("/")
        parts = [p for p in search_date.replace("/", "-").split("-") if p.isdigit()]
        if len(parts) == 1:
            day = int(parts[0])
            today = date.today()
            d = date(today.year, today.month, day)
        elif len(parts) == 3:
            p0, p1, p2 = int(parts[0]), int(parts[1]), int(parts[2])
            if p0 > 31:
                d = date(p0, p1, p2)
            elif p2 > 31:
                d = date(p2, p1, p0)
            else:
                d = date(p2 + 2000 if p2 < 100 else p2, p1, p0)
    except (ValueError, IndexError, TypeError):
        raise HTTPException(400, "Invalid date. Use day (e.g. 18) or DD-MM-YYYY")
    all_students = db.query(Student).filter(Student.role == "student").all()
    total = len(all_students)
    approved = db.query(LeaveRequest).filter(LeaveRequest.status == "Approved").all()
    away_ids = set()
    for lv in approved:
        dep_d = lv.departure_datetime.date() if hasattr(lv.departure_datetime, "date") else lv.departure_datetime
        arr_d = lv.arrival_datetime.date() if hasattr(lv.arrival_datetime, "date") else lv.arrival_datetime
        if dep_d <= d < arr_d:
            away_ids.add(lv.student_id)
    away_count = len(away_ids)
    away_names = [s.name for s in all_students if s.id in away_ids]
    remaining_count = total - away_count
    remaining_names = [s.name for s in all_students if s.id not in away_ids]
    return {
        "date": d.isoformat(),
        "total": total,
        "remaining": remaining_count,
        "away": away_count,
        "away_students": away_names,
        "remaining_students": remaining_names,
        "food_count": remaining_count,
    }


@app.get("/api/leave/all", response_model=list[LeaveRequestResponse])
def all_leave_requests(
    status_filter: str = None,
    user: Student = Depends(get_current_warden),
    db: Session = Depends(get_db),
):
    q = db.query(LeaveRequest).join(Student)
    if status_filter and status_filter.lower() in (
        "parent_pending", "warden_pending", "approved",
        "rejected_by_warden", "rejected_by_parent", "pending"
    ):
        v = status_filter.upper().replace(" ", "_")
        if v == "PENDING":
            q = q.filter(LeaveRequest.status.in_(("Pending", "PARENT_PENDING", "WARDEN_PENDING")))
        else:
            q = q.filter(LeaveRequest.status == v)
    leaves = q.order_by(LeaveRequest.created_at.desc()).all()
    return [
        LeaveRequestResponse(
            id=l.id,
            student_id=l.student_id,
            reason=l.reason,
            departure_datetime=l.departure_datetime,
            arrival_datetime=l.arrival_datetime,
            status=l.status,
            parent_verified=l.parent_verified,
            created_at=l.created_at,
            student_name=l.student.name,
            department=l.student.department,
        )
        for l in leaves
    ]


@app.get("/")
def root():
    return {"message": "Hostel Leave API", "docs": "/docs"}


@app.get("/api/meta/whatsapp-webhook")
async def meta_webhook_verify(mode: str = None, verify_token: str = None, challenge: str = None):
    """Meta webhook verification - WhatsApp requires this for webhook registration."""
    if mode == "subscribe" and verify_token == settings.meta_webhook_verify_token:
        return PlainTextResponse(challenge or "")
    raise HTTPException(403, "Verification failed")


@app.post("/api/meta/whatsapp-webhook")
async def meta_whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Meta WhatsApp webhook - handles button taps and text replies (accept/reject)."""
    try:
        body = await request.json()
        entry = (body.get("entry") or [{}])[0]
        changes = (entry.get("changes") or [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages") or []
        for msg in messages:
            db = SessionLocal()
            try:
                if msg.get("type") == "interactive":
                    interactive = msg.get("interactive", {})
                    btn = interactive.get("button_reply", {}) or interactive.get("list_reply", {})
                    payload = btn.get("id", "")
                    if payload.startswith("approve_"):
                        action, token = "approve", payload[8:]
                    elif payload.startswith("reject_"):
                        action, token = "reject", payload[7:]
                    else:
                        continue
                    leave = db.query(LeaveRequest).filter(LeaveRequest.approval_token == token).first()
                    if leave and not leave.token_used and datetime.utcnow() <= leave.token_expiry:
                        _process_parent_action(db, leave, action, background_tasks)
                elif msg.get("type") == "text":
                    msg_body = (msg.get("text", {}).get("body", "") or "").strip().lower()
                    action = None
                    if msg_body in ("accept", "approve", "yes", "ok", "approved", "yes."):
                        action = "approve"
                    elif msg_body in ("reject", "rejected", "no", "no."):
                        action = "reject"
                    if action:
                        from_num = msg.get("from", "")
                        parent_phone_norm = _normalize_phone_for_lookup("whatsapp:" + str(from_num))
                        last10 = "".join(c for c in parent_phone_norm if c.isdigit())[-10:]
                        all_students = db.query(Student).filter(Student.parent_phone.isnot(None)).all()
                        students = [s for s in all_students if s.parent_phone and "".join(c for c in str(s.parent_phone) if c.isdigit())[-10:] == last10]
                        for stu in students:
                            leave = db.query(LeaveRequest).filter(
                                LeaveRequest.student_id == stu.id,
                                LeaveRequest.status == "PARENT_PENDING",
                                LeaveRequest.token_used == False,
                                LeaveRequest.token_expiry >= datetime.utcnow(),
                            ).order_by(LeaveRequest.created_at.desc()).first()
                            if leave:
                                _process_parent_action(db, leave, action, background_tasks)
                                break
            finally:
                db.close()
    except Exception as e:
        print(f"[Meta Webhook] Error: {e}")
    return {"ok": True}


def _normalize_phone_for_lookup(wa_from: str) -> str:
    """Extract and normalize phone from Twilio From (whatsapp:+919876543210)."""
    if not wa_from:
        return ""
    num = wa_from.replace("whatsapp:", "").strip()
    num = num.lstrip("+").replace(" ", "").replace("-", "")
    if len(num) == 10 and num.isdigit():
        return "+91" + num
    if num.startswith("91") and len(num) == 12:
        return "+" + num
    return "+" + num if num else ""


def _process_parent_action(db, leave, action: str, background_tasks):
    """Shared logic for approve/reject - used by webhook and parent-action."""
    leave.token_used = True
    student = db.query(Student).filter(Student.id == leave.student_id).first()
    if action == "approve":
        leave.status = "WARDEN_PENDING"
        leave.parent_verified = True
        leave.warden_token = secrets.token_urlsafe(32)
        leave.warden_token_expiry = datetime.utcnow() + timedelta(hours=settings.token_expiry_hours)
        db.commit()
        warden_email = settings.warden_email
        async def _send():
            try:
                await send_parent_approved_to_warden(warden_email, student.name, student.department, leave.reason, leave.departure_datetime, leave.arrival_datetime, leave.warden_token)
                print(f"[Webhook] Warden email sent to {warden_email}")
            except Exception as ex:
                import traceback
                print(f"[Webhook SMTP] Warden email FAILED to {warden_email}: {ex}")
                traceback.print_exc()
            try:
                await send_parent_approved_to_student(student.student_email, student.name, leave.departure_datetime)
                print(f"[Webhook] Student notification sent to {student.student_email}")
            except Exception as ex:
                print(f"[Webhook SMTP] Student email failed: {ex}")
        background_tasks.add_task(_send)
    else:
        leave.status = "REJECTED_BY_PARENT"
        db.commit()
        async def _send_rej():
            try:
                await send_parent_rejected_emails(student.student_email, getattr(student, "warden_maylady_email", None) or settings.warden_email)
            except Exception as ex:
                print(f"[Webhook SMTP] {ex}")
        background_tasks.add_task(_send_rej)


@app.post("/api/twilio/whatsapp-webhook")
async def twilio_whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Twilio: 'When a message comes in' - set this URL.
    Handles: 1) Button taps (Content Template), 2) Text reply 'accept'/'reject'."""
    try:
        form = await request.form()
        from_num = form.get("From", "")
        msg_body = (form.get("Body", "") or "").strip()
        button_payload = form.get("ButtonPayload", "")
        print(f"[Twilio Webhook] From={from_num} Body={msg_body[:80] if msg_body else ''} ButtonPayload={button_payload[:50] if button_payload else ''}")
        if button_payload:
            action, token = None, ""
            if button_payload.startswith("approve_"):
                action, token = "approve", button_payload[8:]
            elif button_payload.startswith("reject_"):
                action, token = "reject", button_payload[7:]
            if action and token:
                db = SessionLocal()
                try:
                    leave = db.query(LeaveRequest).filter(LeaveRequest.approval_token == token).first()
                    if leave and not leave.token_used and datetime.utcnow() <= leave.token_expiry:
                        _process_parent_action(db, leave, action, background_tasks)
                finally:
                    db.close()
        elif msg_body:
            action = None
            lower = msg_body.lower().strip()
            if lower in ("accept", "approve", "yes", "ok", "approved", "accept.", "yes."):
                action = "approve"
            elif lower in ("reject", "rejected", "no", "reject.", "no."):
                action = "reject"
            if action:
                parent_phone_norm = _normalize_phone_for_lookup(from_num)
                last10 = "".join(c for c in parent_phone_norm if c.isdigit())[-10:]
                db = SessionLocal()
                try:
                    all_students = db.query(Student).filter(Student.parent_phone.isnot(None)).all()
                    students = [s for s in all_students if s.parent_phone and "".join(c for c in str(s.parent_phone) if c.isdigit())[-10:] == last10]
                    for stu in students:
                        leave = db.query(LeaveRequest).filter(
                            LeaveRequest.student_id == stu.id,
                            LeaveRequest.status == "PARENT_PENDING",
                            LeaveRequest.token_used == False,
                            LeaveRequest.token_expiry >= datetime.utcnow(),
                        ).order_by(LeaveRequest.created_at.desc()).first()
                        if leave:
                            _process_parent_action(db, leave, action, background_tasks)
                            break
                finally:
                    db.close()
    except Exception as e:
        print(f"[Twilio Webhook] Error: {e}")
    return {"ok": True}


@app.get("/api/status")
def api_status():
    """Check if backend has Twilio configured. Open: localhost:8000/api/status"""
    return {
        "twilio_whatsapp": bool(settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from),
        "from_number": settings.twilio_whatsapp_from or "not set",
    }


@app.get("/api/test-whatsapp")
async def test_whatsapp(to: str = None):
    """Test WhatsApp - requires ?to=PHONE (e.g. parent phone). Used to verify Twilio/Meta setup."""
    from whatsapp_service import _send_whatsapp_sync
    import asyncio
    if not to or not to.strip():
        return {"ok": False, "error": "Phone number required. Use ?to=9876543210"}
    to = to.strip()
    body = "Hostel Leave - Test. If you see this, WhatsApp is working!"
    twilio_ok = bool(settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from)
    result = {"twilio_configured": twilio_ok, "to": to}
    if not twilio_ok:
        result["ok"] = False
        result["error"] = "Twilio not configured. Check .env in backend folder."
        return result
    try:
        await asyncio.to_thread(_send_whatsapp_sync, to, body)
        result["ok"] = True
        result["message"] = f"Test sent to {to}. Check WhatsApp on that phone."
        return result
    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)
        return result


@app.get("/api/test-email")
async def test_email():
    """Test SMTP - sends a test email to warden using WARDEN account (same as parent-approve flow)."""
    if not settings.smtp_warden_email or not settings.smtp_warden_password:
        return {"ok": False, "error": "SMTP_WARDEN_EMAIL and SMTP_WARDEN_PASSWORD not set. Add them to backend/.env"}
    try:
        await send_email(
            settings.warden_email,
            "Hostel Leave - Warden Test Email",
            "<p>If you see this, warden SMTP is working! Check Spam if needed.</p>",
            "",
            "warden",
        )
        return {"ok": True, "message": f"Test email sent to {settings.warden_email}. Check inbox (and Spam folder)."}
    except Exception as e:
        return {"ok": False, "error": str(e)}
