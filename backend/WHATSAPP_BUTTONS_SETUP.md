# WhatsApp Interactive Buttons Setup (Approve / Reject)

This guide shows how to get **Approve** and **Reject** buttons in the WhatsApp message (like the Twilio card in the image), instead of plain text links.

---

## Option 1: Twilio Content Template (Recommended for Twilio users)

### Step 1: Create the Template in Twilio Console

1. Go to **Twilio Console** → **Messaging** → **Content** → **Content Template Builder**
2. Click **Create new**
3. Choose **Quick Reply** (or **WhatsApp** → **Quick Reply**)
4. Fill in:
   - **Friendly Name:** `hostel_leave_request`
   - **Body:** `Your child {{1}} requested leave. Reason: {{2}}`
   - **Button 1:**
     - Title: `Approve`
     - ID (payload): `approve_{{3}}`
   - **Button 2:**
     - Title: `Reject`
     - ID (payload): `reject_{{3}}`
5. Add **Sample values** for approval:
   - `{{1}}`: `Aiswarya`
   - `{{2}}`: `Family Function`
   - `{{3}}`: `abc123token`
6. Submit for WhatsApp approval (may take a few hours)
7. After approval, copy the **Content SID** (starts with `HX` or similar)

### Step 2: Configure .env

```
TWILIO_LEAVE_CONTENT_SID=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Webhook for Button Taps

Your Twilio webhook (`/api/twilio/whatsapp-webhook`) already handles button taps. When the parent taps **Approve** or **Reject**, Twilio sends `ButtonPayload` (e.g. `approve_bqePptmm00...`) to your webhook. The backend processes it and sends emails to the warden.

**Important:** The webhook URL must be:
- Publicly accessible (use ngrok for local dev: `ngrok http 8000`)
- Set in Twilio: **Messaging** → **Try it out** → **Try WhatsApp** → **When a message comes in**

---

## Option 2: Meta WhatsApp Cloud API (Interactive Buttons)

If you use **Meta WhatsApp** (not Twilio), the app automatically sends **interactive reply buttons** when possible (within 24-hour session). No template needed.

### Webhook for Meta Button Taps

1. In **Meta Developer Console** → Your App → **WhatsApp** → **Configuration**
2. Set **Webhook URL:** `https://your-backend.com/api/meta/whatsapp-webhook`
3. Set **Verify Token:** Same as `META_WEBHOOK_VERIFY_TOKEN` in .env (default: `hostel-leave-verify`)
4. Subscribe to **messages**

---

## Summary

| Provider | How to get buttons           | Extra config                         |
|----------|-----------------------------|--------------------------------------|
| Twilio   | Create Content Template     | `TWILIO_LEAVE_CONTENT_SID` in .env   |
| Meta     | Automatic (session message) | Webhook at `/api/meta/whatsapp-webhook` |

After setup, parents will see a card with **Approve** (green) and **Reject** (grey) buttons instead of text links.
