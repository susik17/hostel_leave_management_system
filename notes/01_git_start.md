# 🚀 Git, GitHub & SSH - Beginner to DevOps Notes

> Goal: Understand what actually happens when working with Git and GitHub.

---

# 📌 Overall Workflow

                    GitHub Repository
                           │
                 (git clone - First Time)
                           │
                           ▼
                 Local Git Repository
                     (Your Laptop)
                           │
                    Modify Source Code
                           │
                           ▼
                      git status
                           │
                           ▼
                       git add .
                           │
                           ▼
                 Staging Area (Temporary)
                           │
                           ▼
            git commit -m "Added Feature"
                           │
                   Local Commit Created
                           │
                    (Still Local Only)
                           │
                           ▼
                       git push
                           │
                    Authentication
                  (SSH Key / PAT Token)
                           │
                           ▼
                 GitHub Repository Updated

---

# 🌍 Local vs Remote Repository

Remote Repository (GitHub)

hostel_leave_management_system

↓

Stored in GitHub Cloud

-----------------------------

Local Repository (Laptop)

~/hostel_leave_management_system

↓

Editable Source Code

↓

Contains hidden .git folder

Both repositories are **independent**.

Changes made locally DO NOT automatically appear on GitHub.

Changes made on GitHub DO NOT automatically appear on your laptop.

Communication happens only when you run:

- git push
- git pull
- git fetch

---

# 📂 What does git clone actually do?

When you run:

git clone https://github.com/susik17/hostel_leave_management_system.git

Git performs the following:

GitHub
      │
      │ Download Repository
      ▼
Your Laptop

Creates:

hostel_leave_management_system/

├── backend/
├── frontend/
├── README.md
└── .git/

The .git folder stores:

- Commit history
- Branches
- Remote repository URL
- Configuration
- Complete version history

Without .git it is just a normal folder.

---

# 📤 Git Workflow

Step 1

Edit your files.

↓

Step 2

git status

Shows modified files.

↓

Step 3

git add .

Moves files to the Staging Area.

↓

Step 4

git commit -m "message"

Creates a Local Commit.

↓

Step 5

git push

Uploads commits to GitHub.

---

# 🧠 Understanding Staging Area

Working Directory

↓

git add

↓

Staging Area

↓

git commit

↓

Local Repository

↓

git push

↓

GitHub Repository

Think of it like packing a parcel.

Working Directory = Clothes lying on your bed

git add = Put clothes into the suitcase

git commit = Zip the suitcase

git push = Send the suitcase to GitHub

---

# 🔐 HTTPS Authentication

Laptop

↓

HTTPS

↓

GitHub

For Push:

GitHub asks

Who are you?

Old Method

Username + Password

❌ No longer supported.

Current Method

Username + Personal Access Token (PAT)

OR

SSH

---

# 🔑 SSH Authentication

Generate SSH Keys

↓

Private Key

id_ed25519

↓

Stored only on your laptop

↓

Public Key

id_ed25519.pub

↓

Upload to GitHub

↓

GitHub stores your Public Key

↓

Whenever you Push

↓

GitHub verifies

↓

Authentication Successful

---

# 🔐 SSH Directory

~/.ssh/

├── id_ed25519          ← Private Key (Never Share)
├── id_ed25519.pub      ← Public Key (Upload to GitHub)
└── known_hosts         ← Trusted Servers

---

# 🔑 Why do we have two keys?

Private Key

Lives only on your laptop.

Never upload.

Never share.

Public Key

Safe to share.

Uploaded to GitHub.

GitHub uses it only for verification.

---

# 📡 SSH Authentication Flow

Laptop

Private Key
      │
      │
      ▼
GitHub

Stored Public Key
      │
      ▼
Do these keys match?

YES

↓

Push Allowed

NO

↓

Permission denied (publickey)

---

# 🌍 Public vs Private Repository

Public Repository

Anyone can:

✅ View

✅ Clone

✅ Download

❌ Push

unless they have permission.

----------------------------

Private Repository

Only invited users can

View

Clone

Push

---

# 👨‍💻 Repository Permissions

Case 1

Your Repository

Clone

✅

Commit

✅

Push

✅

--------------------------------

Case 2

Someone Else's Public Repository

Clone

✅

Commit

✅

Push

❌

Unless they add you as a Collaborator.

---

# 📥 Clone vs Push

Clone

GitHub

↓

Laptop

Downloads Repository

--------------------------

Push

Laptop

↓

GitHub

Uploads New Commits

---

# 📌 Most Important Commands

Clone Repository

git clone <repo-url>

--------------------------------

Check Status

git status

--------------------------------

Stage Files

git add .

--------------------------------

Create Local Commit

git commit -m "message"

--------------------------------

Upload to GitHub

git push

--------------------------------

Download Latest Changes

git pull

--------------------------------

Check Remote Repository

git remote -v

--------------------------------

Check Git Config

git config --global --list

---

# ⭐ Complete Mental Model

             GitHub Repository
                     │
              git clone
                     │
                     ▼
          Local Git Repository
                     │
             Modify Source Code
                     │
               git status
                     │
                 git add .
                     │
                Staging Area
                     │
                git commit
                     │
              Local Repository
                     │
                 git push
                     │
          SSH Authentication
                     │
                     ▼
             GitHub Repository

Remember:

Clone → Download

Add → Stage

Commit → Save Locally

Push → Upload

Pull → Download Latest Changes

SSH → Authenticate Securely
