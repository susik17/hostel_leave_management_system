"""Run this to test SMTP: py test_smtp.py"""
import smtplib
from email.mime.text import MIMEText
from config import get_settings

s = get_settings()
print("SMTP_USER:", s.smtp_user or "(empty)")
print("SMTP_PASS:", "***" if s.smtp_password else "(empty)")
print("WARDEN_EMAIL:", s.warden_email)
print()

if not s.smtp_user or not s.smtp_password:
    print("ERROR: Add SMTP_USER and SMTP_PASSWORD to backend/.env")
    exit(1)

msg = MIMEText("Hostel Leave - SMTP test. If you see this, email works!")
msg["Subject"] = "Hostel Leave - Test"
msg["From"] = s.smtp_from
msg["To"] = s.warden_email

for port, use_ssl in [(465, True), (587, False)]:
    try:
        print(f"Trying port {port}...")
        if use_ssl:
            with smtplib.SMTP_SSL("smtp.gmail.com", port) as server:
                server.login(s.smtp_user, s.smtp_password)
                server.sendmail(s.smtp_from, s.warden_email, msg.as_string())
        else:
            with smtplib.SMTP("smtp.gmail.com", port) as server:
                server.starttls()
                server.login(s.smtp_user, s.smtp_password)
                server.sendmail(s.smtp_from, s.warden_email, msg.as_string())
        print(f"SUCCESS! Email sent to {s.warden_email}. Check inbox (and Spam).")
        break
    except Exception as e:
        print(f"Port {port} failed: {e}")
else:
    print("\nFAILED. Create new App Password at https://myaccount.google.com/apppasswords")
    print("Update SMTP_PASSWORD in backend/.env and run again.")
