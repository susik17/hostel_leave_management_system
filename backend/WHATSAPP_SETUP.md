# WhatsApp Flow Setup

## New Flow

1. **Student** submits leave from portal
2. **Parent** receives **WhatsApp** with leave details + Approve/Reject links
3. Parent clicks link → opens our page → we process → **Warden** gets email
4. **Warden** clicks Approve in email → **Student** receives **WhatsApp**: "Your leave has been approved. You may go to your hometown."

## Twilio WhatsApp Sandbox Setup

1. Go to **Twilio Console** → **Develop** → **Messaging** → **Try it out** → **Try WhatsApp**
2. Open the **Sandbox** tab
3. **Join the sandbox**: On your (or parent's) WhatsApp, send the join code (e.g. `join row-pair`) to the sandbox number `+1 415 523 8886`
4. Copy the **sandbox "From" number** (e.g. `+14155238886`) and add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_WHATSAPP_FROM=+14155238886
   ```

### Sandbox Settings – "When a message comes in"

**Important:** Replace the default Twilio demo URL with your backend webhook.

1. Go to **Sandbox settings** tab
2. In **"When a message comes in"**:
   - **Local dev (ngrok):** Run `ngrok http 8000`, then set:
     ```
     https://YOUR-NGROK-ID.ngrok-free.app/api/twilio/whatsapp-webhook
     ```
   - **Production:** Use your deployed API URL:
     ```
     https://your-api.com/api/twilio/whatsapp-webhook
     ```
   - **Method:** POST
3. Click **Save**

## Required Fields

- **Parent Phone** (in registration or leave form) – receives leave request on WhatsApp
- **Student Phone** (in registration) – receives "Leave approved" on WhatsApp
- **Warden Maylady Email** – receives parent approval, clicks Approve/Reject

## Fallback

- If Parent Phone is not set: **Email** is sent to parent instead
- If Student Phone is not set: **Email** is sent to student instead
- If Twilio is not configured: **Email only** for all
