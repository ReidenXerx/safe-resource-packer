# 🪟 Windows Launcher Guide (Non-Technical Start Here)

## 🎯 Start Here (Recommended for Beginners)

On Windows, the easiest way to use Safe Resource Packer is to double‑click the launcher. It automatically installs Python and all dependencies, then launches the beautiful Console UI.

-   Double‑click: `run_safe_resource_packer.bat`
-   No command line knowledge needed
-   Auto‑installs Python (if missing) and required packages
-   Guides you step‑by‑step with a friendly interface

If you prefer PowerShell, use `run_safe_resource_packer.ps1` (modern UI, folder picker). If it’s blocked by execution policy, see the Security Settings below.

---

## 🚀 Two Easy Launch Options

### Option 1: Batch File (Recommended)

-   File: `run_safe_resource_packer.bat`
-   Works on Windows XP, 7, 8, 10, 11
-   No execution policy issues
-   Simple double‑click to run

How to use:

1. Double‑click the `.bat` file
2. Follow the colorful menus
3. Choose your option (Interactive UI is recommended)

### Option 2: PowerShell Script (Modern)

-   File: `run_safe_resource_packer.ps1`
-   Richer UI, folder browser support, robust error handling
-   Right‑click → “Run with PowerShell”

If blocked, see Security Settings:

-   Unblock via file Properties → “Unblock” → OK
-   Or run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
-   Or one‑time bypass: `powershell -ExecutionPolicy Bypass -File .\run_safe_resource_packer.ps1`

---

## 🎮 What Each Menu Option Does

1. Interactive Console UI (Beginner‑friendly)

-   Guided menus, no typing required
-   Validates paths and explains options in plain English

2. Quick Classification (Basic mode)

-   Separates files into Pack and Loose folders
-   Fast and simple

3. Complete Packaging (Advanced, but guided)

-   Creates BSA/BA2 + ESP + Loose 7z + final distributable
-   Professional package ready for sharing

4. Install BSArch (Optional but recommended)

-   Helps you install BSArch for optimal BSA/BA2 creation
-   After downloading BSArch from Nexus, the installer finds and sets it up

5. Help & Docs

-   Links to philosophy, usage, troubleshooting

---

## 📁 Choosing Folders (Beginner Tips)

-   Drag & Drop: Drag a folder from Explorer into the launcher window
-   PowerShell “browse”: Type `browse` to open a folder picker
-   Copy & Paste: Paste a path from Explorer’s address bar
-   Manual typing: Include quotes if your path contains spaces

Recommended selections:

-   Source: Your Skyrim/Fallout Data folder (for comparison)
-   Generated: Your BodySlide output folder
-   Output: Any empty folder where results should be written

---

## ✅ Automatic Setup (What the launcher does for you)

-   Checks for Python and installs it if missing
-   Installs Safe Resource Packer and required packages
-   Launches the Console UI with helpful guidance
-   Writes detailed logs to help diagnose issues

No manual environment setup required. Just double‑click and go.

---

## 🚨 Security Settings (PowerShell Only)

If PowerShell blocks the script:

-   File Properties → Unblock
-   Or run as current user: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
-   Or one‑time bypass: `powershell -ExecutionPolicy Bypass -File .\run_safe_resource_packer.ps1`

You can always use the `.bat` launcher to avoid execution policy changes.

---

## 🧩 Troubleshooting

-   “Python not found”: Install from `https://www.python.org/downloads/` (check “Add Python to PATH”) or let the launcher auto‑install
-   “Not enough disk space”: Free up space or target a drive with more room (classification + packaging uses extra temp space)
-   “Path not found”: Use Drag & Drop or the PowerShell folder picker
-   “Access denied”: Try a different output folder or run the launcher as Administrator

---

## 🌍 macOS/Linux (Heads‑up)

This Windows launcher is the simplest path for beginners. On macOS/Linux:

-   Use the release shell script (`Safe_Resource_Packer.sh`) where available; or
-   Install via pip: `pip install safe-resource-packer` and run `safe-resource-packer` (Console UI will guide you)

---

## 🚀 TL;DR for Non‑Technical Users

-   Download the release ZIP
-   Double‑click `run_safe_resource_packer.bat`
-   Follow the on‑screen prompts
-   The launcher installs everything and opens an easy UI
-   Get professional, optimized results in minutes
