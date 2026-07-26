# Git & GitHub - Revision Notes 



# 1. Big Picture
![Git Workflow](images/git_flow01.png)
---

# 2. Git vs GitHub

Git

• Version Control System
• Works Locally
• Tracks File Changes
• Stores History

GitHub

• Cloud Platform
• Stores Remote Repository
• Collaboration
• Backup
• Open Source

Remember

Git != GitHub

Git can work without GitHub.

---

# 3. What is a Repository?

Before Git

Project/

↓

Normal Folder

-----------------------------------

After Git

Project/

├── backend/
├── frontend/
├── README.md
└── .git/

↓

Git Repository

---

# 4. What is .git ?

.git is the brain of Git.

Contains

✓ Commit History

✓ Branches

✓ HEAD

✓ Remote Information

✓ Objects

✓ Configuration

Without .git

↓

Just a normal folder.

---

# 5. Clone

GitHub Repository

↓

git clone

↓

Complete Local Repository

Clone copies

✓ Source Code

✓ Commit History

✓ Branches

✓ Tags

✓ .git Folder

✓ Remote (origin)

Remember

Clone ≠ Copy Paste

---

# 6. Local vs Remote

Local Repository

✓ Edit Code

✓ git status

✓ git add

✓ git commit

-----------------------------------

Remote Repository

✓ git push

✓ git pull

✓ git fetch

Git contacts GitHub ONLY during

• clone

• push

• pull

• fetch

Everything else works locally.

---

# 7. Git Workflow

Edit Code

↓

git status

↓

git add

↓

Staging Area

↓

git commit

↓

Local Commit

↓

git push

↓

GitHub Updated

Quick Hint

Status

↓

Add

↓

Commit

↓

Push

---

# 8. Authentication

HTTPS

Laptop

↓

Username

↓

PAT Token

↓

GitHub

-----------------------------------

SSH

Laptop

↓

Private Key

↓

SSH Authentication

↓

GitHub

↓

Stored Public Key

↓

Authentication Success

Remember

HTTPS → PAT

SSH → Key Pair

---

# 9. SSH Files

~/.ssh/

id_ed25519

↓

Private Key

Never Share

-----------------------------------

id_ed25519.pub

↓

Public Key

Upload to GitHub

-----------------------------------

known_hosts

↓

Trusted Servers

---

# 10. Repository Permissions

Your Repository

Clone

✓

Commit

✓

Push

✓

-----------------------------------

Someone Else's Public Repository

Clone

✓

Commit

✓

Push

✗

Unless you are a Collaborator.

---

# 11. Common Errors

Permission denied (publickey)

↓

SSH Key Missing

-----------------------------------

Password authentication failed

↓

GitHub Password Not Supported

↓

Use PAT / SSH

-----------------------------------

Author identity unknown

↓

git config user.name

git config user.email

-----------------------------------

Nothing to commit

↓

No tracked file changed

OR

Only empty folder created

---

# 12. Important Keywords

Working Directory

↓

Actual Project Files

-----------------------------------

Staging Area

↓

Temporary Area Before Commit

-----------------------------------

Commit

↓

Local Snapshot

-----------------------------------

Repository

↓

Git Managed Folder

-----------------------------------

Origin

↓

Default Remote Repository

-----------------------------------

HEAD

↓

Current Branch Pointer

-----------------------------------

Clone

↓

Download Complete Repository

-----------------------------------

Push

↓

Upload Commits

-----------------------------------

Pull

↓

Download Latest Changes

---

# 13. Interview One-Liners

Git

→ Version Control System

GitHub

→ Cloud Repository Hosting

Clone

→ Creates Complete Local Repository

Commit

→ Saves Changes Locally

Push

→ Uploads Commits to Remote Repository

Pull

→ Downloads Latest Changes

SSH

→ Secure Authentication Using Key Pair

PAT

→ Personal Access Token Used with HTTPS

.git

→ Stores Git Metadata

origin

→ Default Remote Repository

---

# 14. Quick Revision (30 Seconds)

Git

↓

Repository

↓

Clone

↓

Edit

↓

Status

↓

Add

↓

Commit

↓

Push

↓

GitHub

Authentication

HTTPS → PAT

SSH → Private Key + Public Key

Remember

Clone = Download

Commit = Local Save

Push = Upload

Pull = Download

.git = Git Brain

origin = Remote Repository