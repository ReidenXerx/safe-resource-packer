# 🪟 Windows Launcher Guide - For Non-Technical Users

## 🎯 **Perfect for Total Beginners!**

These Windows launchers make Safe Resource Packer **incredibly easy** to use - no command line knowledge required! Just **double-click and go**.

---

## 🚀 **Two Easy Options**

### **Option 1: Batch File (Recommended)**

**File:** `run_safe_resource_packer.bat`

✅ **Advantages:**

-   Works on **ALL** Windows versions (XP, 7, 8, 10, 11)
-   No security restrictions
-   Double-click to run
-   Classic Windows interface

**🖱️ How to Use:**

1. Double-click `run_safe_resource_packer.bat`
2. Follow the colorful menus
3. Choose your option (1-6)
4. Done!

### **Option 2: PowerShell Script (Modern)**

**File:** `run_safe_resource_packer.ps1`

✅ **Advantages:**

-   Modern, colorful interface
-   Better folder picker (browse button)
-   More robust error handling
-   Advanced features

**🖱️ How to Use:**

1. Right-click `run_safe_resource_packer.ps1`
2. Select "Run with PowerShell"
3. If blocked, see "Security Settings" below
4. Follow the beautiful colored menus

---

## 🛡️ **Security Settings (PowerShell Only)**

If PowerShell script is blocked:

**Method 1: Simple Unblock**

1. Right-click `run_safe_resource_packer.ps1`
2. Select "Properties"
3. Check "Unblock" at bottom
4. Click "OK"

**Method 2: Change Execution Policy**

1. Right-click Start button
2. Select "Windows PowerShell (Admin)"
3. Type: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Press Enter, type "Y", press Enter
5. Close PowerShell

**Method 3: Bypass (One-time)**

1. Hold Shift, right-click in folder
2. Select "Open PowerShell window here"
3. Type: `powershell -ExecutionPolicy Bypass -File .\run_safe_resource_packer.ps1`
4. Press Enter

---

## 🎮 **What Each Option Does**

### **1️⃣ Interactive Console UI** _(Recommended for beginners)_

-   Beautiful guided menus
-   No typing required
-   Perfect for first-time users
-   Walks you through everything step-by-step

### **2️⃣ Quick Classification** _(Basic mode)_

-   Just separates files into pack/loose folders
-   Fast and simple
-   Good for basic organization

### **3️⃣ Complete Packaging** _(Advanced mode)_

-   Creates professional mod packages
-   Includes BSA/BA2 archives and ESP files
-   Perfect for sharing mods with others
-   Professional-quality results

### **4️⃣ Install BSArch** _(For optimal performance)_

-   Helps you install BSArch for better BSA/BA2 creation
-   Download from Nexus first, then run this
-   Creates proper game archives instead of ZIP files

### **5️⃣ Help and Documentation**

-   Complete information about the tool
-   Examples and usage guides
-   Performance explanations

---

## 📁 **Folder Selection Made Easy**

Both launchers support **multiple ways** to select folders:

**Drag & Drop:**

-   Drag folder from Windows Explorer
-   Drop into the launcher window
-   Path appears automatically!

**Browse Button (PowerShell only):**

-   Type `browse` when asked for a path
-   Folder picker window opens
-   Select your folder visually

**Copy & Paste:**

-   Copy path from Windows Explorer address bar
-   Paste into launcher
-   Works perfectly!

**Manual Typing:**

-   Type the full path
-   Use quotes if path has spaces
-   Example: `"C:\My Mods\BodySlide Output"`

---

## 🎯 **Typical User Workflow**

### **For BodySlide Users:**

1. Create your BodySlide presets
2. Build your outfits (generates files)
3. Run launcher → Choose option 1 (Interactive UI)
4. Select your Data folder (source)
5. Select your BodySlide output folder (generated)
6. Let the tool work its magic!
7. Get perfectly organized, optimized mod files

### **For Mod Creators:**

1. Create your mod files (textures, meshes, etc.)
2. Run launcher → Choose option 3 (Complete Packaging)
3. Select your folders
4. Enter your mod name
5. Choose your game (Skyrim/Fallout 4)
6. Get professional mod package ready to share!

---

## 🔧 **Prerequisites (Automatic)**

Both launchers **automatically check and install** everything needed:

✅ **Python Detection**

-   Checks if Python is installed
-   Provides download link if missing
-   Warns about PATH requirements

✅ **Package Installation**

-   Automatically installs Safe Resource Packer
-   Shows progress during installation
-   Handles all dependencies

✅ **Ready to Go**

-   Everything set up automatically
-   No manual configuration needed

---

## 💡 **Pro Tips for Beginners**

**🎯 Start Simple:**

-   Use option 1 (Interactive UI) first
-   It guides you through everything
-   No guessing required!

**📁 Organize Your Folders:**

-   Keep source files in one place
-   Keep generated files in another
-   Makes selection easier

**🔄 Try Different Options:**

-   Start with Quick Classification
-   Move to Complete Packaging when ready
-   Each option builds on the previous

**📖 Read the Logs:**

-   Check .log files in output folders
-   Shows exactly what was processed
-   Helps understand what happened

**🎮 Install BSArch:**

-   Download from Nexus Mods
-   Use option 4 to install it
-   Get optimal BSA/BA2 performance

---

## 🚨 **Common Issues & Solutions**

**❌ "Python not found"**

-   Download from: https://www.python.org/downloads/
-   ⚠️ **CRITICAL:** Check "Add Python to PATH" during install
-   Restart launcher after installation

**❌ "PowerShell script blocked"**

-   See "Security Settings" section above
-   Use batch file as alternative
-   Both do the same thing!

**❌ "Installation failed"**

-   Check internet connection
-   Try running as administrator
-   Use batch file if PowerShell fails

**❌ "Path not found"**

-   Check folder exists
-   Remove quotes if manually typed
-   Use drag & drop instead

**❌ "Access denied"**

-   Run as administrator
-   Check folder permissions
-   Try different output location

---

## 🎊 **Success Indicators**

**✅ You'll Know It Worked When:**

-   Colorful success messages appear
-   Log files are created in output folders
-   Pack/Loose folders contain your files
-   Complete packages have .7z files
-   No red error messages

**📁 **Check These Locations:\*\*

-   **Pack folder:** Files ready for BSA/BA2
-   **Loose folder:** Override files
-   **Package folder:** Complete mod packages
-   **Log files:** Detailed processing information

---

## 🎮 **Ready to Optimize Your Mods!**

These launchers transform Safe Resource Packer from a technical tool into a **user-friendly application** that anyone can use. No command line knowledge required - just **double-click and follow the menus**!

**Perfect for:**

-   BodySlide users who want better performance
-   Mod creators who want professional packaging
-   Anyone tired of slow loading times
-   Users who want optimized game files

**🚀 Just double-click and start optimizing! Your game will thank you!** 🎊
