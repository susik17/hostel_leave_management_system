# Hostel Leave Approval System – Full Project Documentation

## 1. Project Overview

A full-stack leave approval system for hostel students. The flow involves three roles:

- **Student** – Submits leave requests
- **Parent** – Approves or rejects via **WhatsApp** (Twilio)
- **Warden** – Gives final approval via **email** or **portal dashboard**

---

## 2. Tech Stack

| Layer    | Technology                 |
|----------|----------------------------|
| Frontend | React (Vite), React Router |
| Backend  | FastAPI (Python)           |
| Database | PostgreSQL / SQLite        |
| WhatsApp | Twilio WhatsApp API        |
| Email    | Gmail SMTP                 |
| Tunnel   | ngrok (for local dev)      |

---

## 3. End-to-End Flow Diagram

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌───────────────┐
│   STUDENT    │     │    PARENT      │     │   WARDEN    │     │   WARDEN      │
│   (Portal)   │     │   (WhatsApp)   │     │   (Email)   │     │   (Portal)    │
└──────┬───────┘     └───────┬───────┘     └──────┬──────┘     └───────┬───────┘
       │                     │                     │                     │
       │ 1. Submit Leave     │                     │                     │
       │    (reason, dates)  │                     │                     │
       │────────────────────>│                     │                     │
       │                     │                     │                     │
       │     2. WhatsApp:     │                     │                     │
       │     "Reply Yes/No"  │                     │                     │
       │<───────────────────>│                     │                     │
       │                     │                     │                     │
       │                     │ 3. Parent replies   │                     │
       │                     │    "Yes" or "No"   │                     │
       │                     │────────┐            │                     │
       │                     │        │ Twilio     │                     │
       │                     │        │ Webhook    │                     │
       │                     │<───────┘            │                     │
       │                     │         (via ngrok) │                     │
       │                     │                     │                     │
       │                     │ 4. Backend:         │                     │
       │                     │    - Update DB      │                     │
       │                     │    - Send email ───>│  5. Email received  │
       │                     │       to warden    │  (or see dashboard)  │
       │                     │                     │                     │
       │ 6. Student sees     │                     │ 7. Warden clicks    │
       │    "Parent Approved │                     │    Approve/Reject   │
       │    – Waiting Warden"│                     │    (email or portal)│
       │<────────────────────│                     │<───────────────────>│
       │                     │                     │                     │
       │ 8. Final status     │                     │                     │
       │    (Approved/Reject)│                     │                     │
       │<───────────────────┴─────────────────────┴─────────────────────┘
```

---

## 4. Detailed Step-by-Step Flow

### Step 1: Student Submits Leave

1. Student logs in at `http://localhost:5175`
2. Fills leave form: reason, departure date, arrival date, parent phone
3. Frontend calls `POST /api/leave` → FastAPI backend
4. Backend:
   - Creates `LeaveRequest` in DB with status `PARENT_PENDING`
   - Generates `approval_token` (24h expiry)
   - Sends **WhatsApp** to parent phone via Twilio
   - If WhatsApp fails → fallback: email to parent

### Step 2: Parent Receives WhatsApp

**Message content (Reply mode):**
```
*Hostel Leave Request*

Your child *Student Name* (Department) has requested hostel leave.

*Reason:* Family function
*Departure:* 23 Feb 2026, 07:11 pm
*Arrival:* 26 Feb 2026, 06:11 pm

Reply *Yes* or *No*
```

Parent must reply **Yes** or **No** (also accepts: accept, approve, ok, reject, no).

### Step 3: Twilio → Webhook (ngrok)

1. Parent replies on WhatsApp
2. Twilio receives the message
3. Twilio sends `POST` to:  
   **`https://YOUR-NGROK-URL.ngrok-free.dev/api/twilio/whatsapp-webhook`**
4. Request goes to ngrok → ngrok forwards to `http://localhost:8000`
5. FastAPI `/api/twilio/whatsapp-webhook` receives the webhook

**Why ngrok?**  
Your backend runs on `localhost:8000`. Twilio is on the internet and cannot reach localhost. ngrok creates a public HTTPS URL that forwards traffic to your local server.

### Step 4: Backend Processes Parent Reply

1. Webhook reads `From` (parent phone) and `Body` (Yes/No)
2. Normalizes phone, finds matching student with `PARENT_PENDING` leave
3. Calls `_process_parent_action(db, leave, action, background_tasks)`:
   - **If approve:** status → `WARDEN_PENDING`, parent_verified → True, create `warden_token`
   - **If reject:** status → `REJECTED_BY_PARENT`
4. Background task runs:
   - Sends **email to warden** (genzovasoftwaresolutions@gmail.com)
   - Sends **email to student** (“Parent approved – waiting for warden”)

### Step 5: Warden Receives Email

**Email subject:** `Parent Approved – Leave Approval Required`  
**Contains:** Student name, department, reason, dates, and **Approve / Reject** buttons linking to:
- `{FRONTEND_URL}/warden-action?token=xxx&type=approve`
- `{FRONTEND_URL}/warden-action?token=xxx&type=reject`

Warden can:
- Click link in email, or
- Log in to Warden Dashboard and Approve/Reject from the portal (refreshes every 10 seconds)

### Step 6: Warden Approves or Rejects

**Via email link:**  
- GET `/api/warden-action?token=xxx&type=approve` (or reject)  
- Backend updates status, sends emails to student and parent

**Via portal:**  
- POST `/api/leave/{id}/approve` or `/api/leave/{id}/reject`  
- Same email notifications

### Step 7: Student Sees Final Status

- **Approved:** Email to student + parent; student sees “Leave Approved”
- **Rejected:** Email to student + parent; student sees “Leave Rejected by Warden”

---

## 5. Twilio WhatsApp – End-to-End

### 5.1 Twilio Setup

1. **Twilio Sandbox**  
   - Console → Messaging → Try it out → Try WhatsApp  
   - Parent must join sandbox: send `join row-pair` (or your code) to `+1 415 523 8886`

2. **Webhook URL**  
   - “When a message comes in”:  
     `https://YOUR-NGROK-URL.ngrok-free.dev/api/twilio/whatsapp-webhook`  
   - Method: **POST**

3. **`.env` variables**
   ```
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_FROM=+14155238886
   ```

### 5.2 Outgoing: Student → Parent

```
Student submits leave
    → Backend (create_leave)
    → whatsapp_service.send_leave_request_to_parent()
    → Twilio API: client.messages.create(from_=whatsapp:+14155238886, to=whatsapp:+91XXXXXXXXXX, body="...")
    → Parent receives WhatsApp
```

### 5.3 Incoming: Parent → Backend

```
Parent replies "Yes"
    → Twilio receives message
    → Twilio POST to ngrok URL
    → ngrok forwards to localhost:8000
    → FastAPI /api/twilio/whatsapp-webhook
    → Parse From, Body → match student → _process_parent_action(approve)
```

### 5.4 Webhook Payload (Twilio)

Twilio sends `application/x-www-form-urlencoded`:

- `From`: `whatsapp:+917539402111`
- `Body`: `Yes` or `No`
- `ButtonPayload`: (if buttons used) `approve_TOKEN` or `reject_TOKEN`

---

## 6. Ngrok – End-to-End

### 6.1 Purpose

- Exposes `localhost:8000` to the internet via a public HTTPS URL
- Twilio needs a public URL for webhooks
- ngrok forwards requests to your local backend

### 6.2 Setup

1. **Install ngrok**  
   - Download from https://ngrok.com/download  
   - Or: `choco install ngrok` (Windows)

2. **Authenticate**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```
   (Get authtoken from dashboard.ngrok.com → Your Authtoken)

3. **Start tunnel**
   ```bash
   ngrok http 8000
   ```

4. **Use the URL**  
   - You get something like: `https://jeanna-accommodable-lovella.ngrok-free.dev`  
   - Twilio webhook: `https://jeanna-accommodable-lovella.ngrok-free.dev/api/twilio/whatsapp-webhook`

### 6.3 Flow

```
Twilio (internet)
    → POST https://xxx.ngrok-free.dev/api/twilio/whatsapp-webhook
    → ngrok cloud
    → ngrok agent on your PC
    → http://localhost:8000/api/twilio/whatsapp-webhook
    → FastAPI
```

### 6.4 Notes

- **Free ngrok URLs change** when you restart ngrok  
- After restart, update Twilio webhook URL
- ngrok “Visit Site” warning: for browser only; Twilio’s POST requests bypass it

---

## 7. Email SMTP – End-to-End

### 7.1 Configuration

**Gmail App Password** (required for SMTP):

1. Google Account → Security → 2-Step Verification (ON)
2. App passwords → Create → name e.g. "warden"
3. Use the 16-character password in `.env` (no spaces)

**`.env` example:**

```
SMTP_WARDEN_EMAIL=genzovasoftwaresolutions@gmail.com
SMTP_WARDEN_PASSWORD=your_16_char_app_password
WARDEN_EMAIL=genzovasoftwaresolutions@gmail.com
```

### 7.2 Email Types and Triggers

| Trigger                  | Recipient | Subject                               | Sender Account |
|--------------------------|-----------|---------------------------------------|----------------|
| Parent approves (webhook) | Warden    | Parent Approved – Leave Approval Required | warden         |
| Parent approves (webhook) | Student   | Parent Approved – Awaiting Warden     | student        |
| Parent approves (link)   | Warden    | (same)                                | warden         |
| Warden approves          | Student   | Leave Approved                         | student        |
| Warden approves          | Parent    | Leave Approved                         | student        |
| Warden rejects           | Student   | Leave Rejected by Warden              | student        |
| Warden rejects           | Parent    | Leave Rejected by Warden              | student        |

### 7.3 Flow (Parent Approve → Warden Email)

```
_process_parent_action(approve)
    → background_tasks.add_task(_send)
    → send_parent_approved_to_warden(warden_email, student_name, ...)
    → email_service.send_email(to=warden_email, from_account="warden")
    → _get_account("warden") → (SMTP_WARDEN_EMAIL, SMTP_WARDEN_PASSWORD)
    → _send_email_sync() → smtplib.SMTP(587) or SMTP_SSL(465)
    → Gmail SMTP sends email to WARDEN_EMAIL
```

### 7.4 Test Endpoint

```
GET http://localhost:8000/api/test-email
```

Sends a test email to warden using the warden SMTP account.

---

## 8. Project Structure

```
priyanga project/
├── backend/
│   ├── main.py              # FastAPI app, routes, webhooks
│   ├── config.py            # Settings from .env
│   ├── email_service.py     # SMTP sending
│   ├── whatsapp_service.py  # Twilio WhatsApp
│   ├── meta_whatsapp_service.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── .env                 # Secrets (never commit)
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LeaveForm.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── WardenDashboard.jsx
│   │   │   ├── ParentAction.jsx
│   │   │   └── WardenAction.jsx
│   │   ├── api.js
│   │   └── ...
│   └── vite.config.js       # Proxy /api → localhost:8000
└── fullproject.md
```

---

## 9. How to Run

### 9.1 Backend

```powershell
cd "c:\Users\Acer\Desktop\priyanga project\backend"
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### 9.2 Frontend

```powershell
cd "c:\Users\Acer\Desktop\priyanga project\frontend"
npm run dev
```

Runs at `http://localhost:5175`.

### 9.3 Ngrok (for Twilio webhook)

```powershell
ngrok http 8000
```

Use the `https://xxx.ngrok-free.dev` URL in Twilio.

---

## 10. Configuration Summary (.env)

| Variable                  | Purpose                          | Example                         |
|---------------------------|----------------------------------|---------------------------------|
| DATABASE_URL              | PostgreSQL connection            | postgresql://user:pass@localhost/db |
| SMTP_WARDEN_EMAIL         | Gmail for sending warden emails  | genzovasoftwaresolutions@gmail.com |
| SMTP_WARDEN_PASSWORD      | Gmail App Password               | xhqrtdwcpwukuwak                 |
| WARDEN_EMAIL              | Recipient of warden emails        | genzovasoftwaresolutions@gmail.com |
| FRONTEND_URL              | Base URL for email links         | http://localhost:5175            |
| TWILIO_ACCOUNT_SID        | Twilio SID                       | AC...                            |
| TWILIO_AUTH_TOKEN         | Twilio token                     | ...                              |
| TWILIO_WHATSAPP_FROM      | Twilio WhatsApp number            | +14155238886                     |
| WHATSAPP_REPLY_MODE       | true = Reply Yes/No              | true                             |

---

## 11. Troubleshooting

### Warden not receiving email

1. Check backend console for `[Webhook] Warden email sent to` or `[Webhook SMTP] Warden email FAILED`
2. Run `GET /api/test-email` and watch console
3. Update `SMTP_WARDEN_PASSWORD` with a fresh App Password
4. Check Spam folder
5. Restart backend after `.env` changes

### Parent WhatsApp not received

1. Parent must join Twilio sandbox: send `join row-pair` to +1 415 523 8886
2. Check `parent_phone` in registration matches WhatsApp number
3. Run `GET /api/test-whatsapp?to=XXXXXXXXXX`

### Twilio webhook not triggered

1. ngrok must be running: `ngrok http 8000`
2. Twilio webhook URL must use current ngrok URL (it changes on restart)
3. Backend must be running on port 8000

### Portal shows "Waiting for Warden" but email sent

1. Warden Dashboard polls every 10 seconds – wait or refresh
2. Default filter: "Warden Pending"
3. Warden can use the email links instead of the portal

---

## 12. Status Flow Summary

```
PARENT_PENDING
    → (Parent replies Yes)  → WARDEN_PENDING  → (Warden approves)  → Approved
    → (Parent replies No)   → REJECTED_BY_PARENT
    → (Warden rejects)      → REJECTED_BY_WARDEN
```

---

*Document generated for Hostel Leave Approval System. Keep this file updated when changing the flow.*



A+ ai3021
O cs3711
A ge3754
A ge3791
A ohs352
O sb8067 

cs3401 a+ 
cs345