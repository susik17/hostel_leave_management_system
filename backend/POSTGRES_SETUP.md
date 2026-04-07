# PostgreSQL Setup

## 1. Create database (optional)
If you want a separate `hostel_leave` database:
- In pgAdmin: right-click Databases → Create → Database → name: `hostel_leave`

Or use your existing `project` database - tables will be in `public` schema.

## 2. Update .env
Edit `backend/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/project
```
Replace `YOUR_PASSWORD` with your PostgreSQL `postgres` user password.
Replace `project` with `hostel_leave` if you created that database.

## 3. Run init
```powershell
cd backend
.\venv\Scripts\Activate.ps1
py init_db.py
```
This creates `students` and `leave_requests` tables in the `public` schema.

## 4. Run backend
```powershell
uvicorn main:app --reload --port 8000
```

---
**Current:** Using SQLite (no password needed). Switch to PostgreSQL when ready.
