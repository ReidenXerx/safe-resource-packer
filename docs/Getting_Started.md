# 🚀 Getting Started with Safe Resource Packer

This guide helps you experience the **revolutionary mod packaging solution** in minutes!

## 🎯 **Choose Your Adventure**

### 🧠 **INTELLIGENT PACKER** - Smart File Classification & Packaging
Transform your BodySlide output into professional mod packages with **AI-powered intelligence** that automatically creates BSA/BA2 archives, ESP files, and distribution packages.

### 📦 **BATCH REPACKER** - Mass Mod Processing Powerhouse
Process entire mod collections automatically - **50+ mods in minutes** instead of days, with consistent professional packaging across your entire collection.

---

## 🎮 **Quick Start (Beginner - Windows)**

**Perfect for non-technical users:**

1. **Download** the latest release from [GitHub Releases](https://github.com/ReidenXerx/safe-resource-packer/releases)
2. **Extract** the ZIP file anywhere
3. **Double-click** `Safe_Resource_Packer.bat`
4. **Done!** The launcher automatically installs Python and all dependencies

**✨ What happens next:**
- ✅ **Zero technical knowledge required**
- ✅ **Automatic Python installation**
- ✅ **Auto-installs all dependencies**
- ✅ **Beautiful guided interface opens**
- ✅ **Drag & drop folder selection**
- ✅ **Built-in help and examples**

If PowerShell blocks `.ps1`, use the `.bat` launcher or see [[Windows_Launcher_Guide]].

---

## ⚙️ **Advanced Installation (Developers)**

**For users who want full control:**

```bash
# Clone the repository
git clone https://github.com/ReidenXerx/safe-resource-packer.git
cd safe-resource-packer

# Install in development mode with all dependencies
pip install -e .

# Or install just the runtime dependencies
pip install -r requirements.txt
```

---

## 🧠 **INTELLIGENT PACKER Examples**

### **One-Command Complete Packaging**
Transform BodySlide output into a professional mod package:

```bash
safe-resource-packer --source ./SkyrimData --generated ./BodySlideOutput \
                     --package ./MyModPackage --mod-name "EpicArmorMod" \
                     --game-type skyrim

# Result: EpicArmorMod_v1.0.7z - Ready for Nexus! 🎉
```

**🎁 What you get:**
- ✅ `EpicArmorMod.esp` - ESP file that loads the archive automatically
- ✅ `EpicArmorMod.bsa` - Optimized game archive (3x faster loading!)
- ✅ `EpicArmorMod_Loose.7z` - Override files (extract separately)
- ✅ Installation instructions and metadata

### **Interactive Console UI (Easiest!)**
**No command-line knowledge required!**

```bash
# Launch beautiful interactive interface
safe-resource-packer

# Or use the dedicated UI command
safe-resource-packer-ui
```

**🎯 The interface will guide you through:**
1. **Selecting your Skyrim Data folder**
2. **Selecting your BodySlide output folder**
3. **Choosing where to save results**
4. **Automatically processing everything!**

---

## 📦 **BATCH REPACKER Examples**

### **Mass Mod Collection Processing**
Process entire mod collections automatically:

```bash
safe-resource-packer --batch-repack --collection ./MyModCollection \
                     --output ./RepackedMods --game-type skyrim

# Result: 50+ professionally packaged mods! 🎉
```

**🎁 What you get:**
- ✅ **Every mod** gets its own optimized BSA/BA2 archive
- ✅ **Proper ESP files** for each mod
- ✅ **Consistent naming** and organization
- ✅ **Professional packaging** for your entire collection

---

## 🎯 **Prerequisites**

- **Python 3.7+** (Windows users can use the portable launcher)
- **Optional**: rich, click, colorama for enhanced CLI experience
- **Disk Space**: ~3x your source folder size for processing
- **RAM**: 4GB minimum, 8GB+ recommended for large mod collections

---

## 🚀 **Next Steps**

### **For Beginners:**
-   See [[Windows_Launcher_Guide]] - One-click Windows setup
-   See [[Console_UI_Guide]] - Interactive interface walkthrough
-   See [[Packaging_Guide]] - Complete BSA/BA2 + ESP + 7z packaging

### **For Power Users:**
-   See [[CLI_Reference]] - All command-line options and examples
-   See [[USAGE]] - Comprehensive usage patterns and scenarios
-   See [[Technical_Deep_Dive]] - How the intelligence works

### **For Troubleshooting:**
-   See [[Debug_Status_Guide]] - Understanding debug output
-   See [[Troubleshooting]] - Common issues and solutions
-   See [[FAQ]] - Frequently asked questions

---

## 🎉 **Ready to Experience the Magic?**

**Safe Resource Packer** transforms your modding workflow from:
- **❌ Chaos** → **✅ Organization**
- **❌ Slow loading** → **✅ 3x faster performance**
- **❌ Manual work** → **✅ One-click automation**
- **❌ Crashes** → **✅ Rock-solid stability**

**🚀 Download now and transform your modding workflow forever!**
