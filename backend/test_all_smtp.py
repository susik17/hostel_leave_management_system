"""Test all 3 SMTP accounts - send 'Hi' to each inbox. Run: py test_all_smtp.py"""
import smtplib
from email.mime.text import MIMEText
from config import get_settings

s = get_settings()

def try_send(label: str, from_email: str, password: str, to_email: str):
    if not from_email or not password:
        print(f"  {label}: SKIP (no credentials)")
        return False
    msg = MIMEText("Hello")
    msg["Subject"] = "Hello"
    msg["From"] = from_email
    msg["To"] = to_email
    for port, use_ssl in [(465, True), (587, False)]:
        try:
            if use_ssl:
                with smtplib.SMTP_SSL("smtp.gmail.com", port) as server:
                    server.login(from_email, password)
                    server.sendmail(from_email, [to_email], msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port) as server:
                    server.starttls()
                    server.login(from_email, password)
                    server.sendmail(from_email, [to_email], msg.as_string())
            print(f"  {label}: OK - sent Hello to {to_email}")
            return True
        except Exception as e:
            err = str(e)[:60]
            print(f"  {label}: FAIL -", err)
    return False

print("Sending 'Hello' from each account to its own inbox...\n")

try_send("Parent", s.smtp_parent_email, s.smtp_parent_password, s.smtp_parent_email)
try_send("Warden", s.smtp_warden_email, s.smtp_warden_password, s.smtp_warden_email)
try_send("Student", s.smtp_student_email, s.smtp_student_password, s.smtp_student_email)

print("\nCheck: hirthicksofficial, genzovasoftwaresolutions, hirthick@student.tce.edu")
