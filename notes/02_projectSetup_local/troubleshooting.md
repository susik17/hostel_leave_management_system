# Phase 2 - Troubleshooting

This file contains the real issues faced during project setup and how they were resolved.

---

# Issue 1 - Missing Python Package

## Error

```text
ModuleNotFoundError: No module named 'bcrypt'
```

## Cause

The project used the `bcrypt` package, but it was not installed.

## Fix

```bash
pip install bcrypt
```

Also update on requirements.txt file .

---

# Issue 2 - Database Schema Mismatch

## Error

```text
sqlite3.OperationalError:
no such column: students.parent_phone
```

## Cause

The application code expected new columns, but the SQLite database was created using an older schema.

## Investigation

Check the database schema.

```bash
sqlite3 hostel_leave.db
```

```sql
.schema students
```

## Solution

Delete the old database.

```bash
rm hostel_leave.db
```

Create a new database.

```bash
python init_db.py
```

Start the backend again.

```bash
uvicorn main:app --reload
```

## Learning

Whenever you see:

- no such table
- no such column
- relation does not exist

Always compare the **application schema** with the **database schema**.

---

# Debugging Flow

```
Application Error
        │
        ▼
Read Last Error
        │
        ▼
Find Root Cause
        │
        ▼
Verify
        │
        ▼
Apply Fix
        │
        ▼
Test Again
```
## Lesson Learned

When errors like these appear:

- no such table
- no such column
- relation does not exist

Always verify the database schema before changing the application code.

---

## Development vs Production

| Development | Production |
|-------------|------------|
| Delete and recreate the database if no important data exists. | Never delete the production database. |
| Quick and simple fix. | Use database migration tools such as Alembic. |
| Suitable for local development. | Suitable for real production systems. |

---