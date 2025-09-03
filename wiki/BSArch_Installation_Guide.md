# 📦 BSArch Installation Guide - Realistic & User-Friendly Approach

## 🎯 **The Problem with Automatic Downloads**

Original approach had issues:

-   ❌ **Nexus requires login** - Can't download directly
-   ❌ **CAPTCHA protection** - Prevents automated access
-   ❌ **Terms of service** - Automated downloads may violate ToS
-   ❌ **File locations change** - URLs become invalid over time

## 🚀 **Our Smart Solution: Guided Manual Setup**

Instead of trying to automate what can't be automated, we **guide users through the process** and **automate everything we can**.

### **🎮 User Experience**

**Step 1: User Downloads**

```
💡 For optimal performance, install BSArch: https://www.nexusmods.com/newvegas/mods/64745?tab=files
💡 Or use: safe-resource-packer --install-bsarch for guided setup
```

**Step 2: We Handle Everything Else**

```bash
safe-resource-packer --install-bsarch
```

**What happens:**

1. 🔍 **Auto-search Downloads folder** - Finds BSArch files automatically
2. 📦 **Extract from archives** - Handles .zip, .7z files intelligently
3. 🔧 **Install to proper location** - Sets up in system directories
4. 🛠️ **Configure PATH** - Makes BSArch globally available
5. ✅ **Verify installation** - Confirms everything works

## 🔍 **Smart Search Strategy**

### **Search Locations (in order):**

1. **Downloads folder** - `~/Downloads`, `C:/Users/*/Downloads`
2. **Desktop** - Common alternative location
3. **System-wide search** - If user agrees (can be slow)

### **Search Patterns (case-insensitive):**

-   `*bsarch*` - Matches any BSArch file
-   `*BSArch*` - Handles different capitalizations
-   `*BSARCH*` - Covers all variations

### **File Types Handled:**

-   **Archives:** `.zip`, `.7z`, `.rar`
-   **Direct executables:** `.exe`
-   **Cross-platform:** Works on Windows, Linux, macOS

## 🛠️ **Technical Implementation**

### **Search Process:**

```python
def find_bsarch_in_downloads(self) -> Optional[str]:
    patterns = ['*bsarch*', '*BSArch*', '*BSARCH*']

    for download_dir in self.common_download_dirs:
        for pattern in patterns:
            # Look for archives first
            for ext in ['.zip', '.7z', '.rar']:
                for file_path in Path(download_dir).glob(pattern + ext):
                    return str(file_path)

            # Look for direct executables
            for file_path in Path(download_dir).glob(pattern + '.exe'):
                return str(file_path)
```

### **Archive Extraction:**

```python
def extract_bsarch_from_archive(self, archive_path: str) -> Optional[str]:
    # Support multiple formats
    if archive_path.lower().endswith('.zip'):
        success = self._extract_zip(archive_path, temp_dir)
    elif archive_path.lower().endswith('.7z'):
        success = self._extract_7z(archive_path, temp_dir)

    # Find BSArch.exe (case-insensitive)
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower() in ['bsarch.exe', 'bsarch']:
                return os.path.join(root, file)
```

### **Installation Process:**

```python
def _install_bsarch_executable(self, source_path: str) -> Tuple[bool, str]:
    # Copy to proper location
    target_path = os.path.join(self.install_dir, target_name)
    shutil.copy2(source_path, target_path)

    # Make executable (Linux/macOS)
    if self.system != 'windows':
        os.chmod(target_path, 0o755)

    # Verify installation
    return self.is_bsarch_available()
```

## 🎯 **User Journey Examples**

### **Scenario 1: Perfect Case**

```
1. User downloads BSArch from Nexus to Downloads folder
2. Runs: safe-resource-packer --install-bsarch
3. Tool finds BSArch.zip automatically
4. Extracts BSArch.exe
5. Installs and configures PATH
6. ✅ Ready to create optimal BSA/BA2 archives!
```

### **Scenario 2: Different Location**

```
1. User downloaded BSArch to Desktop
2. Runs installer
3. Not found in Downloads → searches Desktop
4. Finds and installs successfully
5. ✅ Works perfectly!
```

### **Scenario 3: System-wide Search**

```
1. User has BSArch somewhere on system
2. Runs installer
3. Not found in common locations
4. Tool asks: "Search entire system? (may be slow)"
5. User agrees → finds BSArch anywhere on system
6. ✅ Installation successful!
```

### **Scenario 4: Guidance Needed**

```
1. User runs installer
2. BSArch not found anywhere
3. Tool provides clear instructions:
   - Exact Nexus URL
   - What file to download
   - Where to save it
   - How to run installer again
4. ✅ User knows exactly what to do!
```

## 💡 **Benefits of This Approach**

### **✅ For Users:**

-   **No account sharing** - Users use their own Nexus accounts
-   **Respects ToS** - No automated downloads from Nexus
-   **Works reliably** - Not dependent on changing URLs
-   **Handles variations** - Finds files regardless of naming
-   **Comprehensive search** - Looks everywhere if needed
-   **Clear guidance** - Always knows next steps

### **✅ For Developers:**

-   **Legally compliant** - No ToS violations
-   **Maintainable** - No broken download links
-   **Robust** - Handles many file variations
-   **User-friendly** - Guides through process
-   **Cross-platform** - Works on all systems

### **✅ For Tool Ecosystem:**

-   **Sustainable** - Doesn't rely on external APIs
-   **Respectful** - Doesn't abuse mod hosting sites
-   **Flexible** - Adapts to user preferences
-   **Professional** - Maintains good relationships with modding community

## 🔧 **Installation Commands**

### **Main Installation:**

```bash
# Guided BSArch setup
safe-resource-packer --install-bsarch
```

### **Console UI Integration:**

```bash
# Interactive interface includes BSArch installer
safe-resource-packer
# → Choose "Tools" → "Install BSArch"
```

### **Help and Guidance:**

```bash
# Shows installation instructions
safe-resource-packer --help
# Look for "PACKAGING OPTIONS" section
```

## 📋 **What Users See**

### **Clear Messaging:**

```
⚠️  WARNING: BSA/BA2 creation tools not found!
⚠️  Creating ZIP archive instead of BSA (not optimal for game performance)
💡 For optimal performance, download BSArch: https://www.nexusmods.com/newvegas/mods/64745?tab=files
💡 Or use: safe-resource-packer --install-bsarch for guided setup
```

### **Installation Process:**

```
🔧 Setting up BSArch for optimal BSA/BA2 creation...
🔍 Searching for BSArch in download directories...
✅ Found BSArch file: /home/user/Downloads/BSArch_v0.9.zip
📦 Extracting BSArch from: /home/user/Downloads/BSArch_v0.9.zip
✅ Found BSArch executable: /tmp/bsarch_extract_xyz/BSArch.exe
📋 Copied BSArch to: /home/user/.local/bin/BSArch.exe
🔧 Made BSArch executable
✅ BSArch installed and available!
```

## 🎊 **Perfect Balance**

This approach achieves the **perfect balance** between automation and user control:

-   **Automates everything we can** - Search, extract, install, configure
-   **Respects what we can't** - Manual download from Nexus
-   **Provides clear guidance** - Users always know what to do
-   **Works reliably** - Not dependent on external APIs
-   **Maintains relationships** - Respects modding community norms

**Result:** Users get optimal BSA/BA2 creation with minimal effort and maximum reliability! 🌟
