import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import get_settings

settings = get_settings()
SMTP_TIMEOUT = 15  # seconds - fail fast so we can try next port


def _send_email_sync(to: str, subject: str, html_body: str, text_body: str = "", bcc: str = None,
                     from_email: str = None, from_password: str = None):
    """Send email using specified account. Falls back to SMTP_USER/SMTP_PASSWORD if not set."""
    use_email = from_email or settings.smtp_user
    use_password = from_password or settings.smtp_password
    if not use_email or not use_password:
        msg = f"[SMTP] SKIP - No credentials. Would send to {to}: {subject}"
        print(msg)
        raise ValueError(msg)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = use_email
    msg["To"] = to
    if bcc:
        msg["Bcc"] = bcc
    msg.attach(MIMEText(text_body or html_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    recipients = list(dict.fromkeys([r.strip() for r in to.split(",")] + ([bcc] if bcc else [])))

    last_err = None
    # Try 587 (STARTTLS) first - often more reliable; fallback to 465 (SSL)
    for port, use_ssl in [(587, False), (465, True)]:
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(settings.smtp_host, port, timeout=SMTP_TIMEOUT) as server:
                    server.login(use_email, use_password)
                    server.sendmail(use_email, recipients, msg.as_string())
            else:
                with smtplib.SMTP(settings.smtp_host, port, timeout=SMTP_TIMEOUT) as server:
                    server.starttls()
                    server.login(use_email, use_password)
                    server.sendmail(use_email, recipients, msg.as_string())
            print(f"[SMTP] OK (port {port}) from {use_email} -> {to}" + (f" (BCC: {bcc})" if bcc else "") + f": {subject}")
            return
        except Exception as e:
            last_err = e
            print(f"[SMTP] Port {port} failed for {use_email}: {e}")
    err_msg = f"SMTP failed: {last_err}. Create new App Password: https://myaccount.google.com/apppasswords"
    print(f"[SMTP] {err_msg}")
    raise RuntimeError(err_msg)


def _get_account(which: str):
    """Return (email, password) for parent, warden, or student. Fallback to legacy SMTP_USER/SMTP_PASSWORD."""
    if which == "parent" and settings.smtp_parent_email and settings.smtp_parent_password:
        return settings.smtp_parent_email, settings.smtp_parent_password
    if which == "warden" and settings.smtp_warden_email and settings.smtp_warden_password:
        return settings.smtp_warden_email, settings.smtp_warden_password
    if which == "student" and settings.smtp_student_email and settings.smtp_student_password:
        return settings.smtp_student_email, settings.smtp_student_password
    return settings.smtp_user, settings.smtp_password


async def send_email(to: str, subject: str, html_body: str, text_body: str = "", from_account: str = None):
    em, pw = _get_account(from_account) if from_account else (settings.smtp_user, settings.smtp_password)
    await asyncio.to_thread(_send_email_sync, to, subject, html_body, text_body, None, em, pw)


async def send_email_bcc(to: str, bcc: str, subject: str, html_body: str, text_body: str = "", from_account: str = None):
    em, pw = _get_account(from_account) if from_account else (settings.smtp_user, settings.smtp_password)
    await asyncio.to_thread(_send_email_sync, to, subject, html_body, text_body, bcc, em, pw)


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d %b %Y, %I:%M %p")


async def send_parent_verification_email(
    parent_email: str,
    student_name: str,
    department: str,
    reason: str,
    departure: datetime,
    arrival: datetime,
    token: str,
):
    """Parent receives email with TWO buttons. To Parent ONLY - no BCC."""
    approve_url = f"{settings.frontend_url}/parent-action?token={token}&type=approve"
    reject_url = f"{settings.frontend_url}/parent-action?token={token}&type=reject"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Hostel Leave - Parent Action Required</h2>
        <p>Your child has requested hostel leave. Please click a button below.</p>
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr><td><b>Student Name:</b></td><td>{student_name}</td></tr>
            <tr><td><b>Department:</b></td><td>{department}</td></tr>
            <tr><td><b>Reason (Entered by Student):</b></td><td>{reason}</td></tr>
            <tr><td><b>Departure:</b></td><td>{format_datetime(departure)}</td></tr>
            <tr><td><b>Arrival:</b></td><td>{format_datetime(arrival)}</td></tr>
        </table>
        <p>This link expires in 24 hours. One-time use only.</p>
        <p>
            <a href="{approve_url}" style="background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Approve</a>
            <a href="{reject_url}" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reject</a>
        </p>
    </body>
    </html>
    """
    await send_email(parent_email, "Hostel Leave - Parent Action Required", html, "", "parent")


async def send_parent_approved_to_warden(
    warden_email: str,
    student_name: str,
    department: str,
    reason: str,
    departure: datetime,
    arrival: datetime,
    warden_token: str,
):
    """When parent approves: email to Warden with Approve/Reject buttons."""
    to_email = (warden_email or "").strip() or settings.warden_email
    if not to_email:
        print("[SMTP] SKIP warden email - no recipient (set WARDEN_EMAIL in .env)")
        return
    approve_url = f"{settings.frontend_url}/warden-action?token={warden_token}&type=approve"
    reject_url = f"{settings.frontend_url}/warden-action?token={warden_token}&type=reject"
    PARENT_APPROVAL_MESSAGE = (
        "I hereby confirm that I approve my son/daughter to visit home for the above mentioned reason. "
        "Please review and approve the leave."
    )
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Request – Parent Approved</h2>
        <p><b>Yes, this is your parent approval.</b> Please click a button below.</p>
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr><td><b>Student Name:</b></td><td>{student_name}</td></tr>
            <tr><td><b>Department:</b></td><td>{department}</td></tr>
            <tr><td><b>Reason (Entered by Student):</b></td><td>{reason}</td></tr>
            <tr><td><b>Departure:</b></td><td>{format_datetime(departure)}</td></tr>
            <tr><td><b>Arrival:</b></td><td>{format_datetime(arrival)}</td></tr>
        </table>
        <p><b>Parent Approval Status:</b></p>
        <p>{PARENT_APPROVAL_MESSAGE}</p>
        <p>
            <a href="{approve_url}" style="background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Leave Approved</a>
            <a href="{reject_url}" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Leave Rejected</a>
        </p>
    </body>
    </html>
    """
    await send_email(to_email, "Parent Approved – Leave Approval Required", html, "", "warden")


async def send_parent_approved_to_student(
    student_email: str,
    student_name: str,
    departure: datetime,
):
    """Notify student when parent has approved their leave (awaiting warden)."""
    dep_str = format_datetime(departure)
    html = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Parent Approved Your Leave</h2>
        <p>Hi {student_name},</p>
        <p>Your parent has approved your leave request.</p>
        <p>Departure: {dep_str}</p>
        <p>Warden Maylady will give final approval shortly. You will be notified once approved.</p>
    </body></html>
    """
    await send_email(student_email, "Parent Approved – Awaiting Warden", html, "", "student")


async def send_parent_rejected_emails(
    student_email: str,
    warden_email: str,
):
    """When parent rejects: different emails to Student and Warden."""
    html_student = """
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Rejected by Parent</h2>
        <p>Your parent has declined your leave request.</p>
        <p>You cannot proceed with this leave.</p>
    </body></html>
    """
    html_warden = """
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Rejected by Parent</h2>
        <p>Parent has rejected the leave request.</p>
        <p>No further action required.</p>
    </body></html>
    """
    await asyncio.gather(
        send_email(student_email, "Leave Rejected by Parent", html_student, "", "parent"),
        send_email(warden_email, "Leave Rejected by Parent", html_warden, "", "parent"),
    )


async def send_leave_approved_emails(
    student_email: str,
    parent_email: str,
    student_name: str,
    departure: datetime,
):
    """When warden approves: different messages to Student and Parent."""
    dep_str = format_datetime(departure)
    html_student = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Approved</h2>
        <p>Hi {student_name},</p>
        <p>Your leave request has been officially approved by the warden.</p>
        <p>You may leave hostel on {dep_str}.</p>
    </body></html>
    """
    html_parent = """
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Approved</h2>
        <p>The warden has approved your child's leave.</p>
    </body></html>
    """
    await asyncio.gather(
        send_email(student_email, "Leave Approved", html_student, "", "student"),
        send_email(parent_email, "Leave Approved", html_parent, "", "student"),
    )


async def send_leave_rejected_emails(
    student_email: str,
    parent_email: str,
    student_name: str,
):
    """When warden rejects: different messages to Student and Parent."""
    html_student = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Rejected</h2>
        <p>Hi {student_name},</p>
        <p>Your leave has been rejected by the warden.</p>
        <p>Please contact hostel office.</p>
    </body></html>
    """
    html_parent = """
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Leave Rejected</h2>
        <p>Warden has rejected your child's leave.</p>
    </body></html>
    """
    await asyncio.gather(
        send_email(student_email, "Leave Rejected by Warden", html_student, "", "student"),
        send_email(parent_email, "Leave Rejected by Warden", html_parent, "", "student"),
    )
