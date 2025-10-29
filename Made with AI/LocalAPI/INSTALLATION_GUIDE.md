# Installation Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Complete guide to installing and running LocalAPI.

## System Requirements

### Minimum Requirements
- **OS:** Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- **Node.js:** 18.0.0 or higher
- **RAM:** 4 GB
- **Disk Space:** 500 MB for application + dependencies

### Recommended
- **Node.js:** 20.x LTS
- **RAM:** 8 GB or more
- **Disk Space:** 1 GB

## Prerequisites

### 1. Install Node.js

**Windows:**
1. Download from [nodejs.org](https://nodejs.org/)
2. Run installer (choose LTS version)
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

**macOS:**
```bash
# Using Homebrew
brew install node

# Verify
node --version
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version
```

### 2. Install Build Tools

**Windows:**
```bash
# Option 1: Visual Studio Build Tools (Recommended)
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++"

# Option 2: windows-build-tools (Automated)
npm install --global windows-build-tools
```

**macOS:**
```bash
xcode-select --install
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# Fedora/RHEL
sudo dnf groupinstall "Development Tools"
```

### 3. Install Python 3.x

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3
```

## Installation Steps

### Method 1: Using Setup Script (Recommended)

**Windows:**
```bash
cd LocalAPI
scripts\setup.bat
```

This script will:
- Check Node.js installation
- Install all dependencies
- Verify installation
- Display next steps

### Method 2: Manual Installation

```bash
# 1. Navigate to project directory
cd LocalAPI

# 2. Install dependencies
npm install

# 3. Verify installation
npm run type-check
```

## Running LocalAPI

### Development Mode

**Windows:**
```bash
# Option 1: Using script
scripts\run.bat

# Option 2: Using npm
npm run dev
```

**macOS/Linux:**
```bash
npm run dev
```

This will:
1. Start Vite dev server on http://localhost:5173
2. Launch Electron application
3. Open DevTools automatically
4. Enable hot reload

### Production Build

```bash
# Build application
npm run build

# Package for your platform
npm run package:win    # Windows
npm run package:mac    # macOS
npm run package:linux  # Linux
```

## Verification

### 1. Check Installation
```bash
# Verify Node.js
node --version  # Should be 18+

# Verify npm
npm --version

# Verify dependencies
npm list --depth=0
```

### 2. Run Tests
```bash
# Windows
scripts\test.bat

# macOS/Linux
npm test
```

### 3. Start Application
```bash
npm run dev
```

**Expected Result:**
- Vite dev server starts
- Electron window opens
- Application UI displays
- Theme toggle works
- No console errors

## Troubleshooting

### Issue: "node: command not found"

**Solution:**
- Node.js not installed or not in PATH
- Reinstall Node.js and ensure "Add to PATH" is checked
- Restart terminal/command prompt

### Issue: "npm install" fails with native module errors

**Windows Solution:**
```bash
# Install build tools
npm install --global windows-build-tools

# Clear cache and retry
npm cache clean --force
npm install
```

**macOS Solution:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Retry installation
npm install
```

**Linux Solution:**
```bash
# Install build essentials
sudo apt-get install build-essential python3

# Retry installation
npm install
```

### Issue: "better-sqlite3" fails to install

**Solution:**
```bash
# Rebuild native modules
npm rebuild better-sqlite3

# Or install with specific Python version
npm install --python=python3
```

### Issue: "keytar" fails to install

**Windows:**
- Ensure Visual Studio Build Tools are installed
- Restart terminal as Administrator

**macOS:**
- Install Xcode Command Line Tools
- May require macOS SDK

**Linux:**
```bash
# Install required libraries
sudo apt-get install libsecret-1-dev
```

### Issue: Port 5173 already in use

**Solution:**
```bash
# Find and kill process using port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5173 | xargs kill -9
```

### Issue: Electron window doesn't open

**Solution:**
1. Check console for errors
2. Verify Vite dev server is running
3. Wait for "ready-to-show" event
4. Check firewall settings

### Issue: "Cannot find module" errors

**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Post-Installation

### 1. Configure Application

Copy example config:
```bash
cp config.example.json config.json
```

Edit `config.json` to customize settings.

### 2. First Run

1. Start application: `npm run dev`
2. Check theme toggle works
3. Verify DevTools open
4. Check for console errors

### 3. Create First Request

1. Click "+" in sidebar
2. Enter request name
3. Select GET method
4. Enter URL: `https://jsonplaceholder.typicode.com/users`
5. Click Send
6. View response

## Updating

### Update Dependencies
```bash
# Check for updates
npm outdated

# Update all dependencies
npm update

# Update specific package
npm update <package-name>
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
npm install

# Rebuild if needed
npm run build
```

## Uninstallation

### Remove Application
```bash
# Delete project directory
rm -rf LocalAPI

# Or on Windows
rmdir /s /q LocalAPI
```

### Remove Global Packages (Optional)
```bash
npm uninstall -g windows-build-tools
npm uninstall -g electron
```

## Platform-Specific Notes

### Windows
- Requires Visual Studio Build Tools or windows-build-tools
- May need to run terminal as Administrator
- Antivirus may flag Electron during build

### macOS
- Requires Xcode Command Line Tools
- First run may require security approval
- Gatekeeper may block unsigned builds

### Linux
- Requires build-essential package
- May need additional libraries for native modules
- AppImage format recommended for distribution

## Getting Help

### Resources
- Documentation: `docs/` folder
- Quick Start: `docs/QUICKSTART.md`
- User Guide: `docs/USER_GUIDE.md`
- Troubleshooting: This file

### Common Commands
```bash
# Install dependencies
npm install

# Start development
npm run dev

# Run tests
npm test

# Build production
npm run build

# Package application
npm run package:win

# Type check
npm run type-check

# Lint code
npm run lint
```

## Next Steps

After successful installation:
1. Read [Quick Start Guide](docs/QUICKSTART.md)
2. Review [User Guide](docs/USER_GUIDE.md)
3. Explore [API Documentation](docs/API.md)
4. Try example requests

---

**Need Help?**
- Check [Troubleshooting](#troubleshooting) section
- Review [User Guide](docs/USER_GUIDE.md)
- See [Quick Start](docs/QUICKSTART.md)
