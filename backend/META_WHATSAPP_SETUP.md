# Meta WhatsApp Cloud API Setup

**1,000 free conversations per month** – suitable for small hostels.

## 1. Create Meta App & WhatsApp

1. Go to [developers.facebook.com](https://developers.facebook.com) → **My Apps** → **Create App**
2. Choose **Business** type
3. Add **WhatsApp** product to your app
4. Go to **WhatsApp** → **API Setup**

## 2. Get Credentials

From the API Setup page:
- **Phone number ID** – copy this
- **Access token** – use **Generate** for temporary (24h), or create **System User** for permanent token

## 3. Create Message Templates

Go to **Meta Business Suite** → **WhatsApp Manager** → **Message Templates** → **Create**.

### Leave Request Template
- **Name:** `hostel_leave_request` (use this in .env)
- **Language:** English
- **Category:** Utility
- **Body:**
  ```
  {{1}} has requested hostel leave. Reason: {{2}}. Departure: {{3}}. Click to approve: {{4}} Or reject: {{5}}
  ```
- No buttons needed – links in body
- Submit for approval (usually approved in minutes)

### Leave Approved Template
- **Name:** `leave_approved`
- **Body:**
  ```
  Hi {{1}}, your leave has been approved. Departure: {{2}}. You may go to your hometown.
  ```

## 4. Add to .env

```env
META_WHATSAPP_PHONE_ID=123456789012345
META_WHATSAPP_TOKEN=your_permanent_token
META_WHATSAPP_LEAVE_TEMPLATE=hostel_leave_request
META_WHATSAPP_APPROVED_TEMPLATE=leave_approved
```

## 5. Install

```bash
pip install httpx
```

## Priority

- If **Meta** is configured → uses Meta WhatsApp
- Else if **Twilio** is configured → uses Twilio WhatsApp  
- Else → **email only**
