# WhatsApp & Phone Testing

## Twilio Sandbox Settings (make it correct)

1. Go to **Twilio** → **Messaging** → **Try it out** → **Try WhatsApp** → **Sandbox settings**
2. **"When a message comes in"** – Replace the demo URL (`twil.io/demo-reply`) with your webhook:
   - Run: `ngrok http 8000`
   - Copy your ngrok URL (e.g. `https://abc123.ngrok-free.app`)
   - Set: `https://YOUR-NGROK-ID.ngrok-free.app/api/twilio/whatsapp-webhook`
   - Method: **POST** → **Save**
3. **Sandbox number:** `+1 415 523 8886` | **Join code:** `join row-pair`

## WhatsApp Not Working?

**1. 24-Hour Session Rule (Twilio Sandbox):**  
The parent's number must have messaged the sandbox **within the last 24 hours**. If not:
- Parent sends `join row-pair` to `+1 415 523 8886` again
- Then submit a new leave

**2. Test WhatsApp:** Open in browser (replace with parent's phone):
```
http://localhost:8000/api/test-whatsapp?to=9876543210
```
Check backend terminal for `[WhatsApp] OK` or `[WhatsApp] FAILED` with error details.

**3. Check:** Parent Phone is filled in leave form, parent joined sandbox with "join row-pair".

---

## Links Not Working on Phone?

**Problem:** Approve/Reject links don't work when parent taps them on their phone.

**Cause:** Links use `http://localhost:5175` which only works on your computer, not on the parent's phone.

## Fix: Use ngrok (free)

1. **Install ngrok:** https://ngrok.com/download

2. **Start your app:**
   - Backend: `cd backend && .\venv\Scripts\python.exe -m uvicorn main:app --port 8000`
   - Frontend: `cd frontend && npx vite` (runs on port 5175)

3. **Expose frontend:**
   ```bash
   ngrok http 5175
   ```
   You'll get a URL like `https://abc123.ngrok-free.app`

4. **Update `.env`:**
   ```
   FRONTEND_URL=https://abc123.ngrok-free.app
   ```

5. **Restart backend** so it uses the new URL.

6. **Test:** Submit a new leave. Parent receives WhatsApp with links that work on their phone.

---

**Production:** Deploy your app (e.g. Vercel, Railway) and set `FRONTEND_URL` to your live URL.
