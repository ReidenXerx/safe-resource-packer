# 🧠 Safe Resource Packer

**Intelligent file classifier and BSA/BA2 packer for Bethesda game mods**

[📚 Documentation](docs/) · Beginner on Windows? Use the launcher: double‑click `run_safe_resource_packer.bat`

---

## What This Tool Does

Safe Resource Packer automates the process of classifying and packaging mod files for Skyrim and Fallout 4. It uses SHA1 hashing to compare your generated files against game files, then creates proper BSA/BA2 archives with correct formatting and chunking.

**Core Functionality:**
- Analyzes mod files and classifies them as new, modified, or identical
- Creates properly formatted BSA (Skyrim) or BA2 (Fallout 4) archives
- Generates ESP files that load archives correctly
- Packages everything for distribution
- Processes single mods or entire collections in batch

**What makes it useful:**
- **Accuracy:** SHA1 hashing ensures reliable file comparison
- **Automation:** Handles tedious classification and packaging tasks
- **Correctness:** Creates proper Bethesda archive formats with correct chunking
- **Safety:** Never modifies original files, works on copies
- **Convenience:** Interactive UI or command-line interface

---

## The Two Main Features

### 🧠 Intelligent Packer (Single Mod Processing)

**Use Case:** You've generated custom files (BodySlide output, custom textures, retextured meshes) and need to package them properly.

**What it does:**
1. Scans your generated files
2. Compares each file against vanilla game files using SHA1 hashing
3. Classifies files as:
   - **New** (not in vanilla) → Packs into BSA/BA2
   - **Modified** (different from vanilla) → Keeps as loose override
   - **Identical** (same as vanilla) → Skips (no need to include)
4. Creates proper BSA/BA2 archives with game-specific chunking
5. Generates ESP file that loads archives
6. Packages everything into 7z for distribution

**How to use:**
```bash
# Interactive UI (easiest)
safe-resource-packer

# Command line
safe-resource-packer --source ./SkyrimData --generated ./BodySlideOutput \
                     --package ./MyModPackage --mod-name "MyMod" \
                     --game-type skyrim
```

### 📦 Batch Repacker (Multiple Mods Processing)

**Use Case:** You have a folder containing multiple mods and want to repack them all consistently with proper archives.

**What it does:**
1. Discovers all mods in the folder automatically
2. Identifies plugins (ESP/ESL/ESM) for each mod
3. Creates archives for each mod in parallel
4. Generates proper ESP files
5. Packages each mod consistently

**How to use:**
```bash
# Launch Console UI
safe-resource-packer

# Select: "2. 📦 Batch Mod Repacking" option
# Follow the interactive wizard
```

---

## Installation

### Option 1: Bundled Release (Recommended)

**No Python installation required - everything included**

1. Download `safe-resource-packer-X.X.X-bundled.zip` from [Releases](https://github.com/ReidenXerx/safe-resource-packer/releases)
2. Extract anywhere
3. Double-click `run_safe_resource_packer.bat`

**What's included:** Complete Python environment (~30MB) with all dependencies

### Option 2: Python Installation

**For Python users**

```bash
pip install safe-resource-packer
safe-resource-packer
```

**Requirements:** Python 3.7+, dependencies auto-installed (rich, click, colorama, psutil)

### Option 3: From Source

**For developers**

```bash
git clone https://github.com/ReidenXerx/safe-resource-packer.git
cd safe-resource-packer
pip install -e .
safe-resource-packer
```

---

## Quick Start

### Using the Interactive UI (Easiest)

1. Launch: `safe-resource-packer` or double-click the bat file
2. Choose "Quick Start" (option 1)
3. Point to game Data folder (source reference)
4. Point to your generated files (BodySlide output, etc.)
5. Choose output location
6. Enter mod name and select game
7. Tool does everything automatically

### Using Command Line

```bash
# Complete packaging
safe-resource-packer --source "C:\Skyrim\Data" \
                     --generated "C:\BodySlide\Output" \
                     --package "C:\MyMod" \
                     --mod-name "MyArmor" \
                     --game-type skyrim

# With options
safe-resource-packer --source "./Data" --generated "./Output" \
                     --package "./MyMod" --mod-name "MyMod" \
                     --game-type skyrim --threads 16 --compression 3
```

---

## What You Get

**For single mods:**
- `ModName.bsa` or `ModName.ba2` - Archive with new files
- `ModName.esp` - Plugin that loads the archive
- `ModName_Loose.7z` - Modified files (install separately with higher priority)
- `ModName_v1.0.7z` - Complete package for distribution

**For batch processing:**
- Each mod gets its own archive and ESP
- Consistent naming across collection
- Ready for installation

---

## Features

**Core Features:**
- SHA1-based file classification (cryptographically accurate)
- Automatic BSA/BA2 creation with proper formatting
- ESP generation with correct archive loading
- 7z compression for distribution
- Multi-threaded processing for speed
- Progress tracking with visual feedback

**Game Support:**
- **Skyrim SE/LE:** BSA format with automatic chunking (Textures, Meshes)
- **Fallout 4:** BA2 format with asset type separation (Main, Textures)

**Safety Features:**
- Never modifies original files (works on copies)
- Disk space checking before operations
- Path length validation
- Comprehensive error handling
- Debug logging for troubleshooting

**User Experience:**
- Interactive Console UI (no command-line knowledge needed)
- CLI for advanced users and automation
- Drag-and-drop folder selection
- Clear progress visualization
- Helpful error messages

---

## Game-Specific Details

### Skyrim SE/LE

**Archive Format:** `.bsa`

**Automatic Chunking:**
- `ModName.bsa` - General files
- `ModName - Textures.bsa` - Texture files (.dds)
- `ModName - Meshes.bsa` - Mesh files (.nif)

**Blacklisted Folders** (always kept loose):
- `SKSE/` - Script extender files
- `MCM/` - Mod Configuration Menu
- `Sound/` - Audio files
- `Scripts/` - Script files
- `Interface/` - UI files

### Fallout 4

**Archive Format:** `.ba2`

**Asset Type Separation:**
- `ModName - Main.ba2` - Meshes, misc files
- `ModName - Textures.ba2` - Textures (.dds)

**Blacklisted Folders** (always kept loose):
- `F4SE/` - Script extender files
- `MCM/` - Mod Configuration Menu
- `Sound/` - Audio files
- `Interface/` - UI files

---

## Requirements

**Bundled Release:**
- Windows 7 or later
- Nothing else (Python included)

**Python Installation:**
- Python 3.7+
- Dependencies (auto-installed): rich, click, colorama, psutil

**Optional (Auto-installed):**
- BSArch - For optimal BSA/BA2 creation
- 7-Zip - For compression (auto-detected)

**Disk Space:**
- Approximately 3x your source folder size for processing
- Example: 5GB of files = ~15GB temp space

---

## Command Line Reference

```bash
# Basic usage
safe-resource-packer --source <path> --generated <path> --package <path> \
                     --mod-name <name> --game-type <game>

# All options
--source PATH          Source game Data folder
--generated PATH       Your generated files
--package PATH         Output package location
--mod-name NAME        Mod name (no spaces recommended)
--game-type TYPE       skyrim or fallout4
--game-path PATH       Game installation path
--threads N            Processing threads (default: 8)
--compression N        7z level 0-9 (default: 3)
--debug                Enable debug logging
--interactive          Launch wizard
--install-bsarch       Install BSArch tool
--help                 Show help
```

---

## FAQ

**Q: Will this improve my game performance?**  
A: BSA/BA2 archives can help with load times and reduce file system overhead compared to many loose files, but results vary based on your system and mod setup. This tool automates correct packing - it doesn't guarantee specific performance improvements.

**Q: Is this safe?**  
A: Yes. Never modifies original files, works on copies, open-source for verification. Antivirus may show false positives (common with file processing tools).

**Q: Do I need Python?**  
A: Not with bundled release. Otherwise yes, Python 3.7+.

**Q: Works with Mod Organizer 2?**  
A: Yes. Install packed archives as mods. Install loose files separately with higher priority.

**Q: What about script files?**  
A: Script files and SKSE/F4SE folders are kept loose automatically for compatibility.

**Q: Can I customize blacklist?**  
A: Currently hardcoded (SKSE, MCM, Sound, etc.). May add customization later.

---

## How It Works (Technical)

**File Classification:**
1. Scans generated directory recursively
2. Creates SHA1 hash for each file
3. Searches for matching path in source (case-insensitive)
4. Compares hashes if file exists
5. Classifies as new/modified/identical based on results
6. Checks against blacklist folders

**Archive Creation:**
- Uses BSArch for proper BSA/BA2 format
- Separates files by type (textures, meshes, etc.)
- Applies game-specific chunking rules
- Falls back to ZIP if BSArch unavailable

**Multi-threading:**
- ThreadPoolExecutor for parallel file processing
- Configurable thread count (default: 8)
- Safe concurrency with proper synchronization

---

## Troubleshooting

**Antivirus blocks files:**
- Add folder to antivirus exclusions (false positive)

**Python not found:**
- Use bundled release or install Python 3.7+

**Disk space error:**
- Free up space (needs ~3x generated files size)

**Path too long:**
- Extract to shorter path (e.g., C:\SRP\)

**ESP doesn't load archive:**
- Ensure ESP and archive names match exactly
- ESP must be active in load order

**Loose files not overriding:**
- Install loose files with higher priority in mod manager

---

## Support & Links

**🔗 GitHub:** https://github.com/ReidenXerx/safe-resource-packer  
**📖 Documentation:** See [docs/](docs/) folder  
**🐛 Bug Reports:** GitHub Issues  
**💬 Questions:** GitHub Discussions

**📜 License:** MIT - Free and open-source

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Acknowledgments

- BSArch - For BSA/BA2 archive creation
- Rich library - For beautiful terminal UI
- Click library - For CLI interface
- The modding community

---

**🎯 Automates the tedious, does it correctly, saves you time.**
