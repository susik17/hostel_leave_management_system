# Gmail SMTP Setup (Required for Emails)

## Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Turn ON **2-Step Verification**

## Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select app: **Mail**
3. Select device: **Other** → Name it "Hostel Leave"
4. Click **Generate**
5. Copy the **16-character** password (e.g. `abcd efgh ijkl mnop`)
6. Remove spaces: `abcdefghijklmnop`

## Step 3: Update .env
```env
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=your-gmail@gmail.com
WARDEN_EMAIL=warden@example.com
```

**Important:** Use the SAME Gmail that created the App Password for SMTP_USER.

## Step 4: Test
1. Start backend: `uvicorn main:app --reload --port 8000`
2. Open: http://localhost:8000/api/test-email
3. Check warden inbox. If you see an error, the App Password is wrong - create a new one.

## Troubleshooting
- **"Username and Password not accepted"** → Create a NEW App Password, update .env, restart backend
- **Email not in inbox** → Check Spam folder
- Use the Gmail account that OWNS the App Password as SMTP_USER
