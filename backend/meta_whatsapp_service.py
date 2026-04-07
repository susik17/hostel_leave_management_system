"""Meta WhatsApp Cloud API - 1,000 free conversations/month.
Create templates in Meta Business Suite first. Set META_WHATSAPP_* in .env."""
import asyncio
import json
from config import get_settings

settings = get_settings()
META_GRAPH_URL = "https://graph.facebook.com/v18.0"


def _norm_phone(phone: str) -> str:
    """Return E.164 format without + (e.g. 919876543210)."""
    p = phone.strip().replace(" ", "").replace("-", "")
    if not p:
        return ""
    if p.startswith("+"):
        p = p[1:]
    if not p.startswith("91") and len(p) == 10:
        p = "91" + p
    return p


def _send_meta_whatsapp_sync(to: str, payload: dict) -> bool:
    """Send payload to Meta WhatsApp API. Returns True on success."""
    if not settings.meta_whatsapp_phone_id or not settings.meta_whatsapp_token:
        print("[WhatsApp] SKIP - META_WHATSAPP_PHONE_ID or META_WHATSAPP_TOKEN not set")
        return False
    try:
        import httpx
    except ImportError:
        print("[WhatsApp] SKIP - Install httpx: pip install httpx")
        return False
    to_num = _norm_phone(to)
    if not to_num:
        print("[WhatsApp] Invalid phone number")
        return False
    url = f"{META_GRAPH_URL}/{settings.meta_whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.meta_whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload["to"] = to_num
    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                print(f"[WhatsApp] OK -> {to_num}")
                return True
            err = r.json() if r.content else {}
            print(f"[WhatsApp] Failed {r.status_code}: {err.get('error', r.text)}")
            return False
    except Exception as e:
        print(f"[WhatsApp] Error: {e}")
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
    """Send leave request to parent via Meta WhatsApp. Uses template or fallback text."""
    template = (settings.meta_whatsapp_leave_template or "").strip()
    if template:
        # Template: Body "{{1}} requested leave. Reason: {{2}}. Departure: {{3}}. Approve: {{4}} Reject: {{5}}"
        body_params = [
            {"type": "text", "text": student_name[:200]},
            {"type": "text", "text": (reason[:200] or "-")},
            {"type": "text", "text": departure_str[:50]},
            {"type": "text", "text": approve_url[:500]},
            {"type": "text", "text": reject_url[:500]},
        ]
        payload = {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": settings.meta_whatsapp_lang or "en"},
                "components": [{"type": "body", "parameters": body_params}],
            },
        }
        await asyncio.to_thread(_send_meta_whatsapp_sync, parent_phone, payload)
    elif getattr(settings, "whatsapp_reply_mode", True):
        body = (
            f"*Hostel Leave Request*\n\n"
            f"Your child *{student_name}* ({department}) has requested hostel leave.\n\n"
            f"*Reason:* {reason}\n*Departure:* {departure_str}\n*Arrival:* {arrival_str}\n\n"
            f"Reply *Yes* or *No*"
        )
        await asyncio.to_thread(_send_meta_whatsapp_sync, parent_phone, {"messaging_product": "whatsapp", "type": "text", "text": {"body": body[:4096]}})
        return
    else:
        from urllib.parse import urlparse, parse_qs
        token = ""
        if "/go/a/" in approve_url:
            token = approve_url.split("/go/a/")[-1].split("?")[0].split("/")[0]
        else:
            parsed = urlparse(approve_url)
            token = (parse_qs(parsed.query).get("token") or [""])[0]
        if token and len(token) <= 200:
            payload = {
                "messaging_product": "whatsapp",
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": f"Your child *{student_name}* ({department}) has requested hostel leave.\n\n*Reason:* {reason}\n*Departure:* {departure_str}\n*Arrival:* {arrival_str}"[:1024]},
                    "action": {
                        "buttons": [
                            {"type": "reply", "reply": {"id": f"approve_{token}", "title": "Approve"}},
                            {"type": "reply", "reply": {"id": f"reject_{token}", "title": "Reject"}},
                        ]
                    },
                },
            }
            ok = await asyncio.to_thread(_send_meta_whatsapp_sync, parent_phone, payload)
            if ok:
                return
        body = (
            f"*Hostel Leave Request*\n\n"
            f"Your child *{student_name}* ({department}) has requested hostel leave.\n\n"
            f"*Reason:* {reason}\n*Departure:* {departure_str}\n*Arrival:* {arrival_str}\n\n"
            f"*APPROVE (tap link below):*\n{approve_url}\n\n"
            f"*REJECT (tap link below):*\n{reject_url}"
        )
        await asyncio.to_thread(_send_meta_whatsapp_sync, parent_phone, {"messaging_product": "whatsapp", "type": "text", "text": {"body": body[:4096]}})


async def send_leave_approved_to_student(
    student_phone: str,
    student_name: str,
    departure_str: str,
):
    """Notify student via Meta WhatsApp: leave approved."""
    template = (settings.meta_whatsapp_approved_template or "").strip()
    if template:
        payload = {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": settings.meta_whatsapp_lang or "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": student_name[:200]},
                            {"type": "text", "text": departure_str[:50]},
                        ],
                    }
                ],
            },
        }
    else:
        body = (
            f"*Leave Approved*\n\nHi {student_name},\n\n"
            f"Your leave has been approved by the warden.\n"
            f"Departure: {departure_str}\n\nYou may go to your hometown. Have a safe journey!"
        )
        payload = {
            "messaging_product": "whatsapp",
            "type": "text",
            "text": {"body": body[:4096]},
        }
    await asyncio.to_thread(_send_meta_whatsapp_sync, student_phone, payload)
