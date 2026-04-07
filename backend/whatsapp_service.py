"""Send WhatsApp via Twilio. Parent receives leave request; Student receives approval.
Set TWILIO_* and TWILIO_WHATSAPP_FROM (e.g. whatsapp:+14155238886) in .env.
Join Twilio WhatsApp Sandbox first: Messaging > Try it out > Try WhatsApp.
For interactive Approve/Reject buttons: create Content Template, set TWILIO_LEAVE_CONTENT_SID."""
import asyncio
import json
from config import get_settings

settings = get_settings()


def _safe_print(s: str) -> str:
    """Make string safe for Windows console (charmap can't encode Unicode)."""
    return s.encode("ascii", "replace").decode("ascii")


def _norm_phone(phone: str) -> str:
    """Normalize to E.164: +917530053910 for Indian numbers."""
    p = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not p:
        return ""
    if p.startswith("+"):
        return p
    p = p.lstrip("0")
    if not p or not p.isdigit():
        return "+91" + phone.replace(" ", "")[-10:] if phone else ""
    # Indian: 10 digits
    if len(p) == 10:
        return "+91" + p
    # Already has 91 prefix (12 digits)
    if len(p) == 12 and p.startswith("91"):
        return "+" + p
    # 11 digits starting with 91
    if len(p) == 11 and p.startswith("91"):
        return "+" + p
    return "+91" + p[-10:]


def _send_whatsapp_sync(to: str, body: str):
    """Raises Exception with user-friendly message on Twilio sandbox errors."""
    if not settings.twilio_account_sid or not settings.twilio_auth_token or not settings.twilio_whatsapp_from:
        print(f"[WhatsApp] SKIP - Not configured. Would send to {to}: {body[:50]}...")
        return
    try:
        from twilio.rest import Client
    except ImportError:
        print("[WhatsApp] SKIP - Install twilio: pip install twilio")
        raise RuntimeError("Twilio not installed. Run: pip install twilio")
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    to_wa = "whatsapp:" + _norm_phone(to)
    from_wa = (settings.twilio_whatsapp_from or "").strip()
    if not from_wa:
        print("[WhatsApp] SKIP - TWILIO_WHATSAPP_FROM not set")
        return
    if not from_wa.startswith("whatsapp:"):
        from_wa = "whatsapp:" + from_wa
    print(f"[WhatsApp] Sending to {to_wa} from {from_wa}...")
    try:
        msg = client.messages.create(body=body, from_=from_wa, to=to_wa)
        print(f"[WhatsApp] OK -> {to_wa} (sid={getattr(msg,'sid','')}): {body[:60]}...")
    except Exception as e:
        code = getattr(e, "code", None)
        err_msg = str(e)
        # 63016 = outside 24h window; 21211 = invalid To; 21608 = not opted in
        if code in (63016, 21608, 63007) or "sandbox" in err_msg.lower() or "not a valid" in err_msg.lower() or "24" in err_msg.lower():
            friendly = (
                "Parent must join Twilio sandbox first: On WhatsApp, send 'join row-pair' to +1 415 523 8886. "
                "If already joined, send the join message again (24-hour window may have expired)."
            )
            print(f"[WhatsApp] FAILED to {to} (code={code}): {_safe_print(err_msg)}")
            raise RuntimeError(friendly) from e
        print(f"[WhatsApp] FAILED to {to}: {_safe_print(err_msg)}")
        raise


def _send_leave_content_template_sync(to: str, student_name: str, reason: str, token: str):
    """Send leave request via Twilio Content Template with Approve/Reject buttons."""
    if not settings.twilio_leave_content_sid:
        return False
    try:
        from twilio.rest import Client
    except ImportError:
        return False
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    to_wa = "whatsapp:" + _norm_phone(to)
    from_wa = (settings.twilio_whatsapp_from or "").strip()
    if not from_wa or not from_wa.startswith("whatsapp:"):
        from_wa = "whatsapp:" + from_wa if from_wa else ""
    if not from_wa:
        return False
    content_variables = json.dumps({"1": student_name[:200], "2": (reason or "-")[:200], "3": token[:100]})
    try:
        msg = client.messages.create(
            from_=from_wa,
            to=to_wa,
            content_sid=settings.twilio_leave_content_sid,
            content_variables=content_variables,
        )
        print(f"[WhatsApp] OK (Content Template) -> {to_wa}")
        return True
    except Exception as e:
        print(f"[WhatsApp] Content Template failed: {_safe_print(str(e))}")
        return False


async def send_leave_request_to_parent(
    parent_phone: str,
    student_name: str,
    department: str,
    reason: str,
    departure_str: str,
    arrival_str: str,
    approve_url: str,
    reject_url: str,
):
    """Send leave request via WhatsApp. Reply mode: parent types accept/reject. Link mode: parent taps links."""
    use_reply = getattr(settings, "whatsapp_reply_mode", True)
    if use_reply:
        body = (
            f"*Hostel Leave Request*\n\n"
            f"Your child *{student_name}* ({department}) has requested hostel leave.\n\n"
            f"*Reason:* {reason}\n"
            f"*Departure:* {departure_str}\n"
            f"*Arrival:* {arrival_str}\n\n"
            f"Reply *Yes* or *No*"
        )
        await asyncio.to_thread(_send_whatsapp_sync, parent_phone, body)
        return
    if settings.twilio_account_sid and settings.twilio_whatsapp_from and settings.twilio_leave_content_sid:
        from urllib.parse import urlparse, parse_qs
        token = ""
        if "/go/a/" in approve_url:
            token = approve_url.split("/go/a/")[-1].split("?")[0].split("/")[0]
        else:
            parsed = urlparse(approve_url)
            qs = parse_qs(parsed.query)
            token = (qs.get("token") or [""])[0]
        if token:
            ok = await asyncio.to_thread(_send_leave_content_template_sync, parent_phone, student_name, reason, token)
            if ok:
                return
    body = (
        f"*Hostel Leave Request*\n\n"
        f"Your child *{student_name}* ({department}) has requested hostel leave.\n\n"
        f"*Reason:* {reason}\n"
        f"*Departure:* {departure_str}\n"
        f"*Arrival:* {arrival_str}\n\n"
        f"*APPROVE (tap link below):*\n"
        f"{approve_url}\n\n"
        f"*REJECT (tap link below):*\n"
        f"{reject_url}\n\n"
        f"One-time use, 24 hours. Warden gets email when you approve."
    )
    await asyncio.to_thread(_send_whatsapp_sync, parent_phone, body)


async def send_leave_approved_to_student(
    student_phone: str,
    student_name: str,
    departure_str: str,
):
    """Notify student via WhatsApp: leave approved, you may go to hometown."""
    body = (
        f"*Leave Approved*\n\n"
        f"Hi {student_name},\n\n"
        f"Your leave has been approved by the warden.\n"
        f"Departure: {departure_str}\n\n"
        f"You may go to your hometown. Have a safe journey!"
    )
    await asyncio.to_thread(_send_whatsapp_sync, student_phone, body)
