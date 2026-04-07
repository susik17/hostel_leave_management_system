# Hostel Leave Approval System

Full-stack leave management system: **React** + **FastAPI** + **PostgreSQL** + **SMTP**.

## Quick Start

### 1. Database (PostgreSQL)

Create a database and user:

```sql
CREATE DATABASE hostel_leave;
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `DATABASE_URL`:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/hostel_leave
```

Create tables and default warden:

```bash
python init_db.py
```

Run the API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Default Credentials

| Role   | Reg ID / Email | Password   |
|--------|----------------|------------|
| Warden | warden001      | warden123  |
| Warden | (warden email from .env) | warden123 |

---

## SMTP (Optional)

Without SMTP config, emails are printed to the console. To send real emails, set in `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
WARDEN_EMAIL=warden@hostel.edu
FRONTEND_URL=http://localhost:5173
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

---

## Flow (Single Phone: Parent Only)

1. **Student** registers (parent phone required) → logs in → submits leave via **Portal**
2. **Parent** receives **WhatsApp** (or email fallback) with Approve/Reject links
3. **Parent** clicks Accept or Reject → **Warden** receives **email** immediately
4. **Warden** approves/rejects via email link or Portal dashboard
5. **Student** + **Parent** receive **email**; Student also sees status in Portal

**Contact model:** Only the parent has a mobile phone. Warden and student receive notifications via email and portal.

---

## API Endpoints

| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| POST   | /api/register  | Student registration |
| POST   | /api/login     | Login                |
| GET    | /api/me        | Current user         |
| POST   | /api/leave     | Submit leave (auth)  |
| GET    | /api/leave/my  | My leaves (student) |
| GET    | /api/leave/all | All leaves (warden)  |
| GET    | /api/verify    | Parent approve/reject |
