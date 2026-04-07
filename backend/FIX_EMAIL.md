# Fix Email Not Sending

Gmail rejected the App Password. Follow these steps:

## 1. Create NEW App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in to **hirthickofficial@gmail.com**
3. Click **Select app** → **Mail**
4. Click **Select device** → **Other** → Type "Hostel Leave"
5. Click **Generate**
6. Copy the 16-letter password (e.g. `abcd efgh ijkl mnop`)
7. Remove spaces → `abcdefghijklmnop`

## 2. Update .env
Edit `backend/.env`:
```
SMTP_PASSWORD=your_new_16_char_password
```

## 3. Test
```powershell
cd backend
.\venv\Scripts\Activate.ps1
py test_smtp.py
```
You should see: **SUCCESS! Email sent to...**

## 4. Restart Backend
```powershell
uvicorn main:app --reload --port 8000
```

---
**Note:** Leave requests still save to the database even when email fails. You can use the app; parent/warden just won't get email notifications until SMTP is fixed.
