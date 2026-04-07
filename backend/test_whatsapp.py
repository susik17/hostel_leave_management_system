"""Run this script to test WhatsApp: python test_whatsapp.py
Fixes CWD so .env loads. Prints full Twilio response or error."""
import os
import sys

# Ensure we load from backend directory (where .env lives)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def test_whatsapp(to=None):
    from config import get_settings
    get_settings.cache_clear()  # Fresh load
    settings = get_settings()
    
    print("=== WhatsApp Test ===")
    print(f"TWILIO_ACCOUNT_SID: {'SET' if settings.twilio_account_sid else 'MISSING'}")
    print(f"TWILIO_AUTH_TOKEN: {'SET' if settings.twilio_auth_token else 'MISSING'}")
    print(f"TWILIO_WHATSAPP_FROM: {settings.twilio_whatsapp_from or 'MISSING'}")
    print(f"To: {to}")
    print()
    
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        print("ERROR: Twilio credentials missing in .env")
        return False
    
    try:
        from twilio.rest import Client
    except ImportError:
        print("ERROR: pip install twilio")
        return False
    
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    from_wa = (settings.twilio_whatsapp_from or "").strip()
    if not from_wa.startswith("whatsapp:"):
        from_wa = "whatsapp:" + from_wa
    
    p = to.strip().replace(" ", "").replace("-", "")
    if not p.startswith("+"):
        p = "+91" + p.lstrip("0") if p else ""
    to_wa = "whatsapp:" + p
    
    body = "Hostel Leave - Test. If you see this, WhatsApp works!"
    
    try:
        msg = client.messages.create(body=body, from_=from_wa, to=to_wa)
        print(f"SUCCESS! Message SID: {msg.sid}")
        print(f"Status: {msg.status}")
        print("Check WhatsApp on the phone.")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        if hasattr(e, "code"):
            print(f"Error code: {e.code}")
        if hasattr(e, "msg"):
            print(f"Message: {e.msg}")
        if hasattr(e, "more_info"):
            print(f"More info: {e.more_info}")
        return False

if __name__ == "__main__":
    to = sys.argv[1] if len(sys.argv) > 1 else None
    if not to:
        print("Usage: python test_whatsapp.py <parent_phone>")
        sys.exit(1)
    success = test_whatsapp(to)
    sys.exit(0 if success else 1)
