#!/bin/bash

# ============================================
# AI Website Auditor - Backup Creator
# Creates a complete backup for Windows installation
# ============================================

echo "📦 Creating backup package..."

# Create backup directory
BACKUP_DIR="ai_website_auditor_backup"
mkdir -p $BACKUP_DIR

# 1. Copy all Python files
echo "📁 Copying application files..."
cp app.py $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/
cp run.sh $BACKUP_DIR/
cp .env $BACKUP_DIR/ 2>/dev/null || echo "No .env file found"

# 2. Copy reports (if any)
echo "📊 Copying reports..."
mkdir -p $BACKUP_DIR/reports
cp -r reports/*.html $BACKUP_DIR/reports/ 2>/dev/null || echo "No reports to backup"

# 3. Create Windows installation script
echo "🪟 Creating Windows installation guide..."
cat > $BACKUP_DIR/INSTALL_WINDOWS.md << 'EOF'
# 🚀 AI Website Auditor - Windows 11 Installation Guide

## 📋 Prerequisites
- Windows 11
- Internet connection
- Admin rights

---

## 🪟 STEP 1: Install WSL2 (Windows Subsystem for Linux)

**Open PowerShell as Administrator:**

1. Press **Windows Key**
2. Type `PowerShell`
3. Right-click → **Run as administrator**

**Run this command:**
```powershell
wsl --install
