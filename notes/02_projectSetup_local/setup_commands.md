# Phase 2 Setup Commands

## Clone Project

```bash
git clone <repository-url>
cd hostel_leave_management_system
```

## Backend

```bash
cd backend
```

## Create Virtual Environment

```bash
python3 -m venv venv
```

## Activate Virtual Environment

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Create .env

```bash
cp .env.example .env
```

## Change Database

```text
DATABASE_URL=sqlite:///./hostel_leave.db
```

## Run Backend

```bash
uvicorn main:app --reload
```

## Verify Backend

Open:

http://127.0.0.1:8000/docs

---

## Frontend

```bash
cd ../frontend
```

Install Packages

```bash
npm install
```

Run Frontend

```bash
npm run dev
```

Open

http://localhost:5173

---

## Verify

Backend

http://127.0.0.1:8000/docs

Frontend

http://localhost:5173

Both should open successfully.