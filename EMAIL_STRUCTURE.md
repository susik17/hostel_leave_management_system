# Email Structure – Exact Format

---

## Email 1: Parent Action Required

**When:** After student submits  
**To:** Parent ONLY (no BCC)  
**From:** Parent account  
**Subject:** `Hostel Leave - Parent Action Required`

**Body:**
```
Student Name: [name]
Department: [dept]
Reason (Entered by Student): [reason]
Departure: [date]
Arrival: [date]

[I Approve This Leave]  [I Do Not Approve]
```

---

## Email 2: Parent Approved → Warden

**When:** Parent clicks I Approve  
**To:** Warden ONLY  
**From:** Warden account  
**Subject:** `Parent Approved – Leave Approval Required`

**Body (system-generated, NOT forwarded):**
```
Leave Request – Parent Approved

Student Name: [name]
Department: [dept]
Reason (Entered by Student): [reason]
Departure: [date]
Arrival: [date]

Parent Approval Status:
I hereby confirm that I approve my son/daughter to visit home for the above mentioned reason. Please review and approve the leave.
```

---

## Email 3a: Parent Rejected → Student

**When:** Parent clicks I Do Not Approve  
**To:** Student  
**Subject:** `Leave Rejected by Parent`

**Body:** "Your parent has declined your leave request. You cannot proceed with this leave."

---

## Email 3b: Parent Rejected → Warden

**When:** Parent clicks I Do Not Approve  
**To:** Warden  
**Subject:** `Leave Rejected by Parent`

**Body:** "Parent has rejected the leave request. No further action required."

---

## Email 4a: Warden Approved → Student

**When:** Warden clicks Approve  
**To:** Student  
**Subject:** `Leave Approved`

**Body:** "Your leave has been officially approved."

---

## Email 4b: Warden Approved → Parent

**When:** Warden clicks Approve  
**To:** Parent  
**Subject:** `Leave Approved`

**Body:** "Warden has approved your child's leave."

---

## Email 5a: Warden Rejected → Student

**When:** Warden clicks Reject  
**To:** Student  
**Subject:** `Leave Rejected by Warden`

**Body:** "Your leave has been rejected by the warden."

---

## Email 5b: Warden Rejected → Parent

**When:** Warden clicks Reject  
**To:** Parent  
**Subject:** `Leave Rejected by Warden`

**Body:** "Warden has rejected your child's leave."
