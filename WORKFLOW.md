# Hostel Leave – Flow Overview

## Contact Model (Simplified)

| Role    | Receives via       | Responds via        | Notes                          |
|---------|--------------------|---------------------|--------------------------------|
| Student | Portal + Email     | Portal              | No mobile phone in the system  |
| Parent  | **WhatsApp** (only mobile) | WhatsApp link (Accept/Reject) | **Only phone number in system** |
| Warden  | **Email**          | Email link or Portal| No mobile phone                |

---

## Step 1 — Student Submits Leave

1. Student logs in to **Portal** and submits leave (Reason, Departure, Arrival)
2. Parent phone is required (from registration or leave form)
3. Database: `status = PARENT_PENDING`
4. **Parent** receives **WhatsApp**: "Reply with accept or reject" (or links if reply mode off)
5. **Email** (fallback if WhatsApp fails or no parent phone)

---

## Step 2 — Parent Action

**Reply mode (default):** Parent receives WhatsApp: "Reply with accept to approve or reject to reject." Parent types **accept** or **reject** (any case) and sends. No links, no browser. Warden gets email automatically.

**Link mode** (`WHATSAPP_REPLY_MODE=false`): Parent receives links to tap; opens in browser.

### Parent Approves

- Backend: `status = WARDEN_PENDING`, `parent_verified = TRUE`
- **Warden** receives **email** with Approve/Reject links
- **Student** receives email: "Parent approved, awaiting warden"
- **Student Portal** (10s polling): Blue badge "Parent Approved – Waiting for Warden"

### Parent Rejects

- Backend: `status = REJECTED_BY_PARENT`
- Emails to **Student** and **Warden**
- **Student Portal**: Red "Rejected by Parent"

---

## Step 3 — Warden Reviews

- **Warden** receives **email** (no phone) with Approve/Reject links
- Or logs in to **Portal** → Warden Dashboard

### Warden Approves

- Backend: `status = Approved`
- **Student** receives **email**
- **Parent** receives **email**
- **Student Portal**: Green "Leave Approved"

### Warden Rejects

- Backend: `status = REJECTED_BY_WARDEN`
- Emails to **Student** and **Parent**
- **Student Portal**: Red "Rejected by Warden"

---

## Summary Flow

```
Student (Portal)  →  Parent (WhatsApp)  →  Warden (Email)  →  Student (Email + Portal)
     │                     │                     │
     └─ Submit leave       └─ Accept/Reject      └─ Approve/Reject
                              via link              via link or portal
```

**Only the parent has a mobile phone.** All other notifications use email or the portal.
