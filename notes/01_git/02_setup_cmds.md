# Git Installation

```bash
sudo apt update
sudo apt install git
```

---

# Verify

```bash
git --version
```

---

# Configure Git

```bash
git config --global user.name "Susi K"
git config --global user.email "susikumar1718@gmail.com"
```

Verify

```bash
git config --global --list
```

---

# Generate SSH Key

```bash
ssh-keygen -t ed25519 -C "susikumar1718@gmail.com"
```

Press

ENTER

ENTER

ENTER

---

# Check Keys

```bash
ls -la ~/.ssh
```

---

# Start SSH Agent

```bash
eval "$(ssh-agent -s)"
```

---

# Add Private Key

```bash
ssh-add ~/.ssh/id_ed25519
```

---

# Copy Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy entire output

↓

GitHub

↓

Settings

↓

SSH and GPG Keys

↓

New SSH Key

↓

Paste

---

# Test SSH

```bash
ssh -T git@github.com
```

Expected

```
Hi susik17!

You've successfully authenticated...
```

---

# Clone Repository

```bash
git clone git@github.com:susik17/hostel_leave_management_system.git
```

---

# Existing HTTPS Repository → SSH

```bash
git remote -v
```

```bash
git remote set-url origin git@github.com:susik17/hostel_leave_management_system.git
```

Verify

```bash
git remote -v
```

---

# Daily Commands

```bash
git status
git add .
git commit -m "message"
git push
git pull
```