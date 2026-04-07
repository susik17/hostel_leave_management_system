# Parent Phone & Warden Maylady Setup

## What's New

1. **Parent Phone** – Students enter parent phone; approval link is sent via email + optional SMS.
2. **Warden Maylady** – Each student has a Warden Maylady (email + phone); parent approvals go to her, not the main warden.
3. **WhatsApp Link** – After parent approves, they see a button to notify Warden Maylady via WhatsApp.
4. **Student Notification** – When parent approves, the student gets an email that the request is awaiting warden approval.

## Student Registration (new fields)

- **Parent Phone** – For SMS and WhatsApp.
- **Warden Maylady Email** – Email of the warden for this student.
- **Warden Maylady Phone** – WhatsApp number of the warden for this student.

## Leave Form

- **Parent Phone** (optional) – Override for this request; otherwise uses profile value.
- If parent phone is set and Twilio is configured, an SMS with the approval link is sent.

## SMS (optional – Twilio)

Add to `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_FROM_NUMBER=+1234567890
```

Install: `pip install twilio`

If not configured, SMS is skipped; email still works.

## Migration

Run `python init_db.py` to add new columns to existing databases.
