"""Optional SMS via Twilio. Set TWILIO_* in .env to enable."""
import asyncio
from config import get_settings

settings = get_settings()


def _send_sms_sync(to: str, body: str):
    if not settings.twilio_account_sid or not settings.twilio_auth_token or not settings.twilio_from_number:
        print(f"[SMS] SKIP - Twilio not configured. Would send to {to}: {body[:50]}...")
        return
    try:
        try:
            from twilio.rest import Client
        except ImportError:
            print("[SMS] SKIP - Install twilio: pip install twilio")
            return
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        to_clean = to.strip().replace(" ", "")
        if not to_clean.startswith("+"):
            to_clean = "+91" + to_clean.lstrip("0") if to_clean else ""
        client.messages.create(body=body, from_=settings.twilio_from_number, to=to_clean)
        print(f"[SMS] OK -> {to_clean}: {body[:40]}...")
    except Exception as e:
        print(f"[SMS] Failed to {to}: {e}")


async def send_sms_to_parent(parent_phone: str, student_name: str, reason: str, approve_url: str, reject_url: str):
    """Send SMS to parent with approval links (reason + links to approve/reject)."""
    body = (
        f"Hostel Leave: {student_name} requests leave - {reason[:80]}...\n"
        f"Approve: {approve_url}\nReject: {reject_url}"
    )
    await asyncio.to_thread(_send_sms_sync, parent_phone, body)
