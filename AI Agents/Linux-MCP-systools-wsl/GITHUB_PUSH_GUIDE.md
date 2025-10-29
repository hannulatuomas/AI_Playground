# 📦 GitHub Push Instructions

## Quick Setup Guide

### Step 1: Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in the details:
   - **Repository name:** `Linux-MCP-systools-wsl`
   - **Description:** "Kali Linux MCP Server with 37 comprehensive system tools"
   - **Visibility:** ✅ **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click **"Create repository"**

### Step 2: Choose Authentication Method

#### Option A: HTTPS (Recommended for beginners)

```bash
cd ~/mcp-bash-server  # or current location
git remote add origin https://github.com/YOUR_USERNAME/Linux-MCP-systools-wsl.git
git branch -M main
git push -u origin main
```

**Note:** You'll be prompted for your GitHub username and password (use Personal Access Token instead of password).

#### Option B: SSH (Recommended for frequent use)

```bash
cd ~/mcp-bash-server  # or current location
git remote add origin git@github.com:YOUR_USERNAME/Linux-MCP-systools-wsl.git
git branch -M main
git push -u origin main
```

**Note:** Requires SSH key setup (see below).

---

## 🔑 GitHub Authentication Setup

### For HTTPS (Personal Access Token)

GitHub no longer accepts passwords for authentication. You need to create a Personal Access Token:

1. Go to **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Linux-MCP-systools-wsl`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

### For SSH (Public Key)

If you don't have an SSH key:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Display public key
cat ~/.ssh/id_ed25519.pub
```

Add the key to GitHub:
1. Go to **https://github.com/settings/keys**
2. Click **"New SSH key"**
3. Paste your public key
4. Click **"Add SSH key"**

---

## 🚀 Complete Push Commands

From the current directory (`/mnt/c/Users/Coder/Downloads/ClaudeDesktop`):

```bash
# 1. Verify git status
git status

# 2. Add remote (choose HTTPS or SSH)
# HTTPS:
git remote add origin https://github.com/YOUR_USERNAME/Linux-MCP-systools-wsl.git

# OR SSH:
git remote add origin git@github.com:YOUR_USERNAME/Linux-MCP-systools-wsl.git

# 3. Rename branch to 'main' (optional, modern standard)
git branch -M main

# 4. Push to GitHub
git push -u origin main
```

---

## 📋 What's Being Pushed

The following files will be uploaded to your private repository:

```
✓ .gitignore                  # Git ignore rules
✓ README.md                   # Full documentation
✓ QUICK_REFERENCE.md         # Quick reference guide
✓ PROJECT_SUMMARY.md         # Project overview
✓ VISUAL_SUMMARY.txt         # Visual summary
✓ server.py                  # Main MCP server
✓ setup.sh                   # Setup script
✓ push_to_github.sh          # This push helper
✓ tools/__init__.py          # Package init
✓ tools/shell_tools.py       # 3 shell tools
✓ tools/file_tools.py        # 10 file tools
✓ tools/filesystem_tools.py  # 3 filesystem tools
✓ tools/text_tools.py        # 3 text tools
✓ tools/network_tools.py     # 6 network tools
✓ tools/archive_tools.py     # 5 archive tools
✓ tools/system_tools.py      # 7 system tools

Total: 15 files, ~4,010 lines of code
```

**Note:** `__pycache__/` directories are automatically ignored by `.gitignore`

---

## 🔍 Verify Push

After pushing, verify everything is on GitHub:

```bash
# View remote URL
git remote -v

# Check branch
git branch -a

# View commit history
git log --oneline
```

Visit your repository:
```
https://github.com/YOUR_USERNAME/Linux-MCP-systools-wsl
```

---

## 🛠️ Common Issues & Solutions

### Issue: "remote origin already exists"
```bash
# View current remote
git remote -v

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/Linux-MCP-systools-wsl.git
```

### Issue: "Authentication failed"
- For HTTPS: Use Personal Access Token (not password)
- For SSH: Verify SSH key is added to GitHub

### Issue: "Permission denied (publickey)"
```bash
# Test SSH connection
ssh -T git@github.com

# Should see: "Hi USERNAME! You've successfully authenticated..."
```

### Issue: "Branch 'master' vs 'main'"
```bash
# Rename branch
git branch -M main

# Push to main
git push -u origin main
```

---

## 📝 After First Push

### Add Collaborators (if needed)
1. Go to repository settings
2. Click "Collaborators"
3. Add team members

### Protect Main Branch (recommended)
1. Go to Settings → Branches
2. Add branch protection rule for `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks

### Add Repository Topics
Add topics to make it discoverable:
- `mcp-server`
- `kali-linux`
- `python`
- `linux-tools`
- `system-administration`

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `git status` | Check current status |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Commit changes |
| `git push` | Push to GitHub |
| `git pull` | Pull from GitHub |
| `git log` | View commit history |
| `git branch` | List branches |
| `git remote -v` | View remotes |

---

## ✅ Checklist

Before pushing:
- [ ] Created private GitHub repository
- [ ] Set up authentication (Token or SSH)
- [ ] Configured git remote
- [ ] Verified all files are staged
- [ ] Ready to push

After pushing:
- [ ] Verify repository is private
- [ ] Check all files uploaded correctly
- [ ] README displays properly
- [ ] Update repository description
- [ ] Add topics/tags

---

**Repository:** Linux-MCP-systools-wsl  
**Version:** 4.0.0  
**Visibility:** Private  
**License:** MIT
