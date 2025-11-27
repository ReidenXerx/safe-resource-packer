# Safe Resource Packer - Project Knowledge Base

**Last Updated:** 2025-11-27  
**Version:** 1.1.3  
**Purpose:** Complete context for AI assistants and developers working on this project

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Development Setup](#development-setup)
6. [Key Concepts](#key-concepts)
7. [Important Files & Their Roles](#important-files--their-roles)
8. [Data Flow](#data-flow)
9. [Code Patterns & Conventions](#code-patterns--conventions)
10. [Known Issues & Quirks](#known-issues--quirks)
11. [Common Tasks](#common-tasks)
12. [Testing](#testing)
13. [Troubleshooting](#troubleshooting)
14. [Build & Release](#build--release)

---

## 📖 Project Overview

**Safe Resource Packer** is an intelligent file classifier and archive packer designed specifically for Bethesda game modding (Skyrim, Fallout 4). It automates the tedious process of comparing mod files against vanilla game files, classifying them, and packaging them into proper BSA/BA2 archives with correct formatting.

### Core Problem Solved:

When creating mods (especially with tools like BodySlide), you often generate thousands of files. You need to:
1. Identify which files are identical to vanilla (can be skipped)
2. Identify which files are modified from vanilla (must stay loose for priority)
3. Identify which files are completely new (can be packed into archives)
4. Pack new files into proper BSA/BA2 format with correct chunking
5. Generate ESP files that load the archives
6. Package everything for distribution

This tool automates **all of that** using SHA1 hashing for cryptographic accuracy.

### User Personas:

1. **BodySlide Users:** Generate custom body/outfit meshes, need to package them properly
2. **Texture Authors:** Create retextures, need to identify what's new vs. modified
3. **Mod Authors:** Want to distribute mods with proper archives for performance
4. **Mod Collection Curators:** Need to repack multiple mods consistently

### Core Functionality:

#### 🧠 **Intelligent Packer (Single Mod Mode)**
- **Purpose:** Process one mod at a time with full classification
- **Input:** Source Data folder + Generated files folder
- **Output:** Packaged mod with BSA/BA2 + ESP + Loose files (7z archives)
- **Classification:** SHA1-based comparison (new/modified/identical)
- **Use Case:** BodySlide outputs, custom mods, texture packs

#### 📦 **Batch Repacker (Multiple Mod Mode)**
- **Purpose:** Mass-process entire folders of mods
- **Input:** Folder containing multiple mod subdirectories
- **Output:** Each mod repacked with BSA/BA2 + ESP
- **Classification:** Packs everything (no comparison needed)
- **Use Case:** Mod collections, consistent repacking, distribution prep

---

## 🏗️ Architecture

### High-Level Architecture:

```
┌──────────────────────────────────────────────────────────────────┐
│                   Safe Resource Packer                            │
│                                                                   │
│  ┌────────────────────┐         ┌──────────────────────────┐    │
│  │  Console UI        │         │  Enhanced CLI            │    │
│  │  (Interactive)     │         │  (Automation)            │    │
│  └────────────────────┘         └──────────────────────────┘    │
│           │                              │                        │
│           └──────────────┬───────────────┘                        │
│                          │                                        │
│                          ▼                                        │
│               ┌──────────────────────┐                           │
│               │  Core Orchestrator   │                           │
│               │  (SafeResourcePacker)│                           │
│               └──────────────────────┘                           │
│                          │                                        │
│      ┌───────────────────┼────────────────────┐                 │
│      │                   │                    │                  │
│      ▼                   ▼                    ▼                  │
│  ┌─────────┐     ┌──────────────┐    ┌───────────────┐         │
│  │Classifier│     │BatchRepacker │    │PackageBuilder │         │
│  │(SHA1)    │     │(Multi-mod)   │    │(BSA/BA2+ESP)  │         │
│  └─────────┘     └──────────────┘    └───────────────┘         │
│      │                   │                    │                  │
│      └───────────────────┼────────────────────┘                 │
│                          │                                        │
│      ┌───────────────────┼────────────────────┐                 │
│      │                   │                    │                  │
│      ▼                   ▼                    ▼                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐         │
│  │ArchiveCreator│  │CompressionSvc│  │    ESP Manager │         │
│  │(BSArch/ZIP)  │  │(7z CLI)      │  │  (Templates)   │         │
│  └─────────────┘  └──────────────┘  └────────────────┘         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ BSArch  │    │ 7z CLI   │    │ Game Data│
    │(External)│   │(External)│    │ (Source) │
    └─────────┘    └──────────┘    └──────────┘
```

### Key Components:

1. **User Interfaces**
   - **Console UI:** Rich-based interactive menu system
   - **Enhanced CLI:** Command-line for automation and scripting
   - **Wizards:** Step-by-step guides for complex operations

2. **Core Processing**
   - **SafeResourcePacker:** Main orchestrator, thread management
   - **PathClassifier:** SHA1 hashing, file comparison, classification
   - **BatchModRepacker:** Multi-mod discovery and processing

3. **Packaging System**
   - **ArchiveCreator:** BSA/BA2 creation via BSArch or ZIP fallback
   - **ESP Manager:** Template-based ESP generation
   - **PackageBuilder:** Complete packaging pipeline
   - **CompressionService:** Unified 7z CLI compression

4. **External Tools**
   - **BSArch:** Optimal BSA/BA2 creation (auto-installed)
   - **7-Zip:** Cross-platform compression (auto-detected)
   - **Game Data:** Source of truth for vanilla files

---

## 🛠️ Technology Stack

### Core Language & Runtime

- **Language:** Python 3.7+
- **Package Manager:** pip
- **Distribution:** Wheel (`.whl`) + Bundled release (portable)

### Key Dependencies

```python
# User Interface & Output
rich>=13.0.0          # Terminal UI, progress bars, formatting
click>=8.0.0          # CLI framework, command parsing
colorama>=0.4.4       # Cross-platform ANSI colors

# System & Utilities
psutil>=5.8.0         # Disk space, system info
```

### External Tools (Auto-managed)

- **BSArch:** BSA/BA2 archive creation (Windows executable)
- **7-Zip:** Cross-platform compression (`7z` CLI)

### Python Standard Library (Heavy Usage)

```python
# Core Modules
hashlib               # SHA1 hashing
concurrent.futures    # Multi-threading (ThreadPoolExecutor)
tempfile             # Safe temporary directories
shutil               # File operations, tree copying
pathlib              # Modern path handling

# Archive & Compression
zipfile              # Fallback archive creation
subprocess           # External tool execution (BSArch, 7z)

# Configuration & Data
json                 # Config files, user profiles
configparser         # INI-style config reading
```

### Development & Build

```python
# Build System
setuptools>=45       # Package building
wheel                # Binary distribution
build                # PEP 517 build tool

# Project Configuration
pyproject.toml       # Modern Python packaging
setup.py             # Setuptools configuration
MANIFEST.in          # Include non-Python files
```

---

## 📁 Project Structure

```
safe-resource-packer/
├── src/
│   └── safe_resource_packer/
│       ├── __init__.py                   # Package version, exports
│       ├── __main__.py                   # CLI entry point
│       ├── core.py                       # 🔥 Main orchestrator
│       ├── classifier.py                 # 🔥 SHA1 classification logic
│       ├── batch_repacker.py             # 🔥 Multi-mod processing
│       ├── enhanced_cli.py               # CLI interface (Click)
│       ├── console_ui.py                 # Interactive UI (Rich)
│       ├── constants.py                  # Global constants, blacklists
│       ├── utils.py                      # Shared utilities
│       ├── dynamic_progress.py           # Progress tracking, logging
│       ├── comprehensive_logging.py      # Debug logging system
│       ├── game_scanner.py               # Game installation detection
│       ├── bsarch_service.py             # BSArch tool management
│       ├── bsarch_detector.py            # BSArch installation detection
│       ├── config_service.py             # Configuration management
│       ├── config_cache.py               # Config caching
│       │
│       ├── onboarding/                   # First-run experience
│       │   ├── first_time_detector.py    # Detect first run
│       │   ├── user_profiler.py          # User profile, game detection
│       │   └── welcome_system.py         # Welcome screens
│       │
│       ├── guides/                       # Interactive guides
│       │   ├── data_preparation.py       # Help users set up
│       │   ├── results_guide.py          # Explain results
│       │   └── troubleshooting.py        # Common problems
│       │
│       ├── ui/                           # UI components
│       │   ├── quick_start_wizard.py     # Single mod wizard
│       │   ├── batch_repack_wizard.py    # Batch mode wizard
│       │   └── ui_utilities.py           # Shared UI helpers
│       │
│       ├── packaging/                    # Packaging pipeline
│       │   ├── archive_creator.py        # 🔥 BSA/BA2 creation
│       │   ├── esp_manager.py            # ESP generation
│       │   ├── package_builder.py        # 🔥 Complete packaging
│       │   ├── compression_service.py    # 🔥 7z CLI wrapper
│       │   └── bsarch_installer.py       # BSArch auto-install
│       │
│       ├── tutorials/                    # Interactive tutorials
│       │   ├── interactive_tutorial.py   # Step-by-step guide
│       │   ├── example_data.py           # Demo data
│       │   └── comprehension_checks.py   # Quiz system
│       │
│       └── templates/                    # Template files
│           └── esp/
│               ├── skyrim_template.esp   # Skyrim ESP template
│               ├── fallout4_template.esp # Fallout 4 ESP template
│               └── README.md             # Template docs
│
├── docs/                                 # 📚 Complete documentation
│   ├── Getting_Started.md
│   ├── Installation.md
│   ├── CLI_Reference.md
│   ├── API.md
│   ├── Packaging_Guide.md
│   ├── MO2_Integration_Guide.md
│   ├── Console_UI_Guide.md
│   ├── Troubleshooting.md
│   ├── FAQ.md
│   ├── Build_Guide.md
│   ├── Security_Guide.md
│   ├── NEXUS_BRIEF_DESCRIPTION.txt       # Nexus Mods short desc
│   ├── NEXUS_DESCRIPTION_BBCODE.txt      # Nexus Mods formatted desc
│   └── NEXUS_DOCUMENTATION.txt           # Nexus Mods full manual
│
├── release/                              # Built releases
│   ├── safe-resource-packer-X.X.X-bundled.zip
│   └── release_info.json
│
├── dist/                                 # Build artifacts (wheels)
│   ├── safe_resource_packer-X.X.X-py3-none-any.whl
│   └── safe_resource_packer-X.X.X.tar.gz
│
├── tests/                                # Unit tests
│   ├── test_core.py
│   ├── test_classifier.py
│   └── test_utils.py
│
├── examples/                             # Usage examples
│   ├── basic_usage.py
│   ├── batch_repacking_demo.py
│   ├── complete_packaging_demo.py
│   └── ...
│
├── build_release.py                      # 🔥 Release build script
├── run_safe_resource_packer.bat          # Windows launcher
├── run_script.py                         # Python launcher wrapper
│
├── pyproject.toml                        # Modern Python config
├── setup.py                              # Setuptools config
├── MANIFEST.in                           # Include templates
├── requirements.txt                      # Dependencies
│
├── README.md                             # Main documentation
├── CHANGELOG.md                          # Version history
├── LICENSE                               # MIT License
├── PROJECT_KNOWLEDGE.md                  # This file
└── .gitignore                            # Git exclusions
```

### 🔥 Critical Files (Must Understand):

1. **`core.py`** - Main orchestrator, threading, classification flow
2. **`classifier.py`** - SHA1 hashing, file comparison logic
3. **`batch_repacker.py`** - Multi-mod discovery and processing
4. **`packaging/archive_creator.py`** - BSA/BA2 creation with BSArch
5. **`packaging/package_builder.py`** - Complete packaging pipeline
6. **`packaging/compression_service.py`** - 7z CLI wrapper, integrity testing
7. **`console_ui.py`** - Main interactive interface
8. **`build_release.py`** - Bundled release creation

---

## 🚀 Development Setup

### Prerequisites:

- **Python:** 3.7+ (tested with 3.7, 3.8, 3.9, 3.10, 3.11)
- **Git:** For version control
- **7-Zip:** Recommended for testing compression

### First-Time Setup:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/safe-resource-packer.git
cd safe-resource-packer

# 2. Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install in editable mode (for development)
pip install -e .

# 5. Verify installation
safe-resource-packer --version
safe-resource-packer --help
```

### Development Workflow:

```bash
# Run from source (during development)
python -m safe_resource_packer

# Run console UI
safe-resource-packer-ui

# Run with CLI arguments
safe-resource-packer --source ./Data --generated ./Output \
                     --package ./MyMod --mod-name "TestMod" \
                     --game-type skyrim --debug

# Run tests
python -m pytest tests/

# Build wheel
python -m build --wheel

# Build bundled release
python build_release.py
```

### IDE Configuration:

**VS Code (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.rulers": [88],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

---

## 🔑 Key Concepts

### 1. **SHA1-Based File Classification**

**The Core Innovation:** Instead of relying on file paths or timestamps, this tool uses cryptographic hashing (SHA1) to determine if files are truly different.

```python
# Classification Logic:
def classify_file(generated_file, source_dir):
    generated_hash = sha1(generated_file)
    source_file = find_in_source(generated_file_path, source_dir)
    
    if not source_file:
        return "NEW"  # Pack into BSA/BA2
    
    source_hash = sha1(source_file)
    
    if generated_hash == source_hash:
        return "IDENTICAL"  # Skip completely
    else:
        return "MODIFIED"  # Keep loose for priority
```

**Why This Matters:**
- **Accuracy:** Byte-perfect comparison, no false positives
- **Reliability:** Works even with renamed/moved files
- **Performance:** Fast enough for 100,000+ files with threading

**Code Location:** `src/safe_resource_packer/classifier.py`

### 2. **Blacklist System (Unpackable Folders)**

**Critical Concept:** Not all files should go into archives. Some MUST stay loose for game compatibility.

**Blacklisted Folders (Always Loose):**
```python
# Universal blacklist
UNPACKABLE_FOLDERS = {
    'Scripts',       # Papyrus scripts
    'Source',        # Script source
    'Interface',     # UI files
    'SKSE', 'F4SE',  # Script extender
    'SKSEVR', 'F4SEVR',  # VR script extenders
    'MCM',           # Mod Configuration Menu
    'Sound',         # Audio files
}

# Game-specific additions
GAME_SPECIFIC_UNPACKABLE_FOLDERS = {
    'skyrim': ['SKSE', 'SkyUI'],
    'skyrimvr': ['SKSEVR'],
    'fallout4': ['F4SE'],
    'fallout4vr': ['F4SEVR'],
}
```

**Why These Stay Loose:**
- Script extenders require loose files
- MCM needs loose files for menu detection
- Some load order priority issues with archives

**Code Location:** `src/safe_resource_packer/constants.py`

### 3. **BSA Chunking (Skyrim Only)**

**Skyrim-Specific Feature:** Large BSA files cause performance issues. Solution: split by asset type.

```python
# Automatic chunking for Skyrim:
ModName.bsa                  # General files
ModName - Textures.bsa       # All .dds files
ModName - Meshes.bsa         # All .nif files
```

**Chunking Logic:**
```python
def should_chunk(game_type):
    return game_type in ("skyrim", "skyrimvr")

def get_chunk_name(file_path):
    ext = file_path.lower().split('.')[-1]
    if ext in ('dds', 'tga'):
        return "Textures"
    elif ext in ('nif', 'tri'):
        return "Meshes"
    else:
        return None  # Goes to main BSA
```

**Fallout 4:** Uses BA2 format with automatic asset type separation (no manual chunking needed)

**Code Location:** `src/safe_resource_packer/packaging/archive_creator.py`

### 4. **ESP Generation & Archive Loading**

**Critical for Archives to Work:** BSA/BA2 files **only load** if an ESP/ESL/ESM references them.

**ESP Structure:**
```python
# Minimal ESP that loads archives:
1. Form ID: 0x0 (empty plugin)
2. File Name: Must match archive base name
3. Archive Flag: Set to enable archive loading

# Naming requirement:
ModName.esp  +  ModName.bsa  = ✅ Loads
ModName.esp  +  OtherName.bsa = ❌ Won't load
```

**Template System:**
```python
templates/
├── skyrim_template.esp      # Skyrim SE/LE template
└── fallout4_template.esp    # Fallout 4 template

# Usage:
template = load_template(game_type)
new_esp = template.copy()
new_esp.set_name(mod_name)
new_esp.save()
```

**Code Location:** `src/safe_resource_packer/packaging/esp_manager.py`

### 5. **Two-Stage Packaging (Packable + Loose)**

**Important Pattern:** Final output has **two separate archives**, not one combined package.

```python
# Output structure:
ModName/
├── ModName_v1.0.7z          # Main package (BSA/BA2 + ESP)
│   ├── ModName.bsa
│   ├── ModName - Textures.bsa  (if chunking)
│   └── ModName.esp
│
└── ModName_Loose.7z          # Modified files (higher priority)
    ├── meshes/
    ├── textures/
    └── ...
```

**Why Separate?**
- User installs main package normally
- User installs loose files with **higher priority** (overrides archives)
- Correct load order: Archives (low) → Loose files (high)

**Code Location:** `src/safe_resource_packer/packaging/package_builder.py`

### 6. **Thread Safety & Concurrency**

**Performance Strategy:** SHA1 hashing is CPU-intensive, so we use multi-threading.

```python
# Thread pool for classification:
with ThreadPoolExecutor(max_workers=threads) as executor:
    futures = {
        executor.submit(classify_file, file): file
        for file in all_files
    }
    
    for future in as_completed(futures):
        result = future.result()  # Thread-safe
        with self.lock:  # Lock for shared data
            results.append(result)
```

**Thread-Safe Patterns:**
- `threading.Lock()` for shared data structures
- `concurrent.futures` for safe thread management
- No global state modification without locks

**Code Location:** `src/safe_resource_packer/core.py`, `classifier.py`

### 7. **7z Integrity Testing & File Handle Management**

**Critical Fix (v1.1.3):** Large BSA/BA2 files caused corrupted 7z archives on Windows.

**Problem:** `subprocess.run()` returned before 7z fully released file handles.

**Solution:** Promise-like subprocess management + explicit file handle release:

```python
# OLD (unreliable):
result = subprocess.run(['7z', 'a', archive, files], ...)
# Returns too early, file handles still open!

# NEW (reliable):
process = subprocess.Popen(['7z', 'a', archive, files], ...)
stdout, stderr = process.communicate()  # Wait for completion
process.wait()  # Explicit termination wait
time.sleep(2)  # OS file handle release

# Windows-specific file buffer flush:
with open(archive, 'rb') as f:
    f.seek(0, 2)  # Force flush

# Integrity test:
test_result = subprocess.run(['7z', 't', '-slt', archive], ...)
if "Everything is Ok" not in test_result.stdout:
    raise CorruptedArchiveError()
```

**Total Wait Time:** ~5-6 seconds of strategic delays for reliability

**Code Location:** `src/safe_resource_packer/packaging/compression_service.py`, `package_builder.py`

### 8. **Recursion Guard Pattern**

**Bug Fixed in v1.1.2:** Infinite recursion on startup due to circular dependencies.

```python
class UserProfiler:
    def __init__(self):
        self._loading_profile = False  # Recursion guard
    
    def load_user_profile(self):
        if self._loading_profile:  # Check guard
            return {}  # Bail out
        
        self._loading_profile = True
        try:
            # ... actual loading logic
            self.detect_games()  # Might call load_user_profile
        finally:
            self._loading_profile = False  # Always reset
```

**Pattern Used For:**
- Circular profile loading (fixed)
- Prevent infinite loops in any mutually recursive functions

**Code Location:** `src/safe_resource_packer/onboarding/user_profiler.py`

### 9. **Game Type Abstraction**

**Design Pattern:** All game-specific logic abstracted behind game type parameter.

```python
# Unified interface:
packer = SafeResourcePacker(game_type="skyrim")  # or "fallout4"
archive_creator = ArchiveCreator(game_type="fallout4vr")

# Internally:
def get_archive_extension(game_type):
    if game_type in ("fallout4", "fallout4vr"):
        return ".ba2"
    else:  # skyrim, skyrimvr, skyrimle
        return ".bsa"

def supports_chunking(game_type):
    return game_type in ("skyrim", "skyrimvr")
```

**Supported Games:**
- `skyrim` - Skyrim SE/LE
- `skyrimvr` - Skyrim VR
- `fallout4` - Fallout 4
- `fallout4vr` - Fallout 4 VR

**Code Location:** All modules use consistent `game_type` parameter

### 10. **User Profile & Game Detection**

**First-Run Experience:** Automatically detects installed games, saves preferences.

```python
# Profile structure (stored in user home):
~/.safe_resource_packer_profile.json
{
  "version": "1.1.3",
  "games": {
    "skyrim": "C:/SkyrimSE/Data",
    "fallout4": "C:/Fallout4/Data"
  },
  "preferences": {
    "threads": 8,
    "compression": 3,
    "last_mod_name": "MyMod"
  },
  "experience_level": "intermediate"
}
```

**Detection Methods:**
1. **Steam Registry** (Windows)
2. **Common Paths** (`C:/Program Files/Steam/...`)
3. **Vortex Config** (if installed)
4. **Full Drive Search** (last resort, slow)

**Code Location:** `src/safe_resource_packer/onboarding/user_profiler.py`, `game_scanner.py`

---

## 📄 Important Files & Their Roles

### Core Processing Files:

| File | Purpose | Critical Functions |
|------|---------|-------------------|
| **`core.py`** | Main orchestrator | `process_single_mod_resources()`, `copy_folder_to_temp()` |
| **`classifier.py`** | SHA1 classification | `classify_paths()`, `classify_file()`, `copy_file()` |
| **`batch_repacker.py`** | Multi-mod processing | `discover_mods()`, `process_batch()`, `create_mod_archives()` |

### Packaging Files:

| File | Purpose | Critical Functions |
|------|---------|-------------------|
| **`archive_creator.py`** | BSA/BA2 creation | `create_archive()`, `create_chunked_archives()` |
| **`esp_manager.py`** | ESP generation | `create_esp_from_template()`, `set_esp_properties()` |
| **`package_builder.py`** | Complete pipeline | `build_package()`, `_test_archive_integrity()` |
| **`compression_service.py`** | 7z CLI wrapper | `compress_directory()`, `_test_archive_integrity()` |

### UI Files:

| File | Purpose | Entry Points |
|------|---------|--------------|
| **`console_ui.py`** | Rich interactive UI | `run_console_ui()`, `show_main_menu()` |
| **`enhanced_cli.py`** | Click CLI | `enhanced_main()`, CLI decorators |
| **`quick_start_wizard.py`** | Single mod wizard | `QuickStartWizard.run()` |
| **`batch_repack_wizard.py`** | Batch wizard | `BatchRepackWizard.run()` |

### Configuration & Setup:

| File | Purpose | Key Data |
|------|---------|----------|
| **`constants.py`** | Global constants | `UNPACKABLE_FOLDERS`, `GAME_SPECIFIC_*` |
| **`user_profiler.py`** | User profile | Game paths, preferences, detection |
| **`config_service.py`** | Config management | Load/save configurations |
| **`bsarch_service.py`** | BSArch management | Auto-install, detection |

### Build & Release:

| File | Purpose | What It Does |
|------|---------|--------------|
| **`build_release.py`** | Release builder | Creates bundled release with Python |
| **`pyproject.toml`** | Package metadata | Modern Python packaging config |
| **`setup.py`** | Setuptools config | Traditional packaging, version parsing |
| **`MANIFEST.in`** | Include files | Ensures ESP templates are packaged |

---

## 🔄 Data Flow

### Single Mod Processing (Intelligent Packer):

```
User Input
├── Source: Game/Data folder (vanilla reference)
├── Generated: BodySlide output / mod files
├── Package: Output destination
└── Mod Name: For ESP and archive naming

                    ↓

1. Copy Source to Temp (Smart Selective)
   └── Only copy directories that exist in Generated
       (HUGE optimization: 5GB instead of 50GB)

                    ↓

2. Classify Files (SHA1 Hashing)
   ├── For each file in Generated:
   │   ├── Calculate SHA1 hash
   │   ├── Find in Source (case-insensitive)
   │   ├── Compare hashes
   │   └── Classify: NEW / MODIFIED / IDENTICAL
   └── Result: Three file lists

                    ↓

3. Filter by Blacklist
   ├── NEW files:
   │   ├── Check if in blacklist folder → Loose
   │   └── Not blacklisted → Packable
   └── MODIFIED files: → Always loose

                    ↓

4. Create Archives (Packable Files)
   ├── If Skyrim: Check chunking
   │   ├── Separate: Textures / Meshes / Other
   │   └── Create: Main.bsa, Textures.bsa, Meshes.bsa
   └── If Fallout 4:
       ├── Separate: Textures / Main
       └── Create: Main.ba2, Textures.ba2

                    ↓

5. Generate ESP
   ├── Load template (game-specific)
   ├── Set mod name
   └── Save ESP with archive references

                    ↓

6. Package for Distribution
   ├── Package 1: ModName_v1.0.7z
   │   ├── BSA/BA2 files
   │   └── ESP file
   └── Package 2: ModName_Loose.7z
       └── Modified files (user installs with higher priority)

                    ↓

Final Output: Two 7z archives ready for sharing
```

### Batch Mod Processing (Batch Repacker):

```
User Input
├── Collection Folder: Folder containing multiple mod subfolders
└── Game Type: skyrim / fallout4

                    ↓

1. Discover Mods
   ├── Scan collection folder
   ├── For each subfolder:
   │   ├── Find plugins (.esp/.esm/.esl)
   │   ├── Identify asset folders (meshes/, textures/, etc.)
   │   └── Create ModInfo object
   └── Return: List of discovered mods

                    ↓

2. User Selection (Interactive)
   ├── Show discovered mods
   ├── User selects plugin for each mod (if multiple)
   └── User confirms processing

                    ↓

3. Process Each Mod (Parallel)
   ├── For each mod:
   │   ├── Identify packable assets
   │   ├── Create BSA/BA2 archives
   │   ├── Copy/update ESP
   │   └── Move to output folder
   └── Track: Processed / Failed

                    ↓

4. Report Results
   ├── Show statistics
   │   ├── Total mods processed
   │   ├── Archives created
   │   └── Failures (if any)
   └── Output location

                    ↓

Final Output: Folder with repacked mods (BSA+ESP each)
```

### Archive Integrity Flow (v1.1.3+):

```
Create Archive
    ↓
Execute 7z Command
    ↓
Wait for Process (Popen.communicate)
    ↓
Explicit Process Wait
    ↓
Sleep 2 seconds (file handle release)
    ↓
Check Archive Exists
    ↓
Windows File Buffer Flush
    ↓
Sleep 1 second
    ↓
Run 7z Test (-slt detailed)
    ↓
Check "Everything is Ok" in output
    ↓
Success / Raise CorruptedArchiveError
```

---

## 💻 Code Patterns & Conventions

### 1. **Function Naming Convention**

**Critical Pattern:** Function names indicate which mode they belong to:

```python
# Single mod mode (Intelligent Packer):
def single_mod_classify(...)  # Used only for single mod processing
def single_mod_package(...)

# Batch mode (Batch Repacker):
def batch_repack_discover(...)  # Used only for batch processing
def batch_repack_archive(...)

# Shared utilities (no prefix):
def file_hash(...)  # Used by both modes
def safe_walk(...)
```

**Why:** Avoids confusion when reading code, makes mode boundaries clear.

### 2. **Error Handling Pattern**

```python
# Standard pattern throughout codebase:
try:
    result = do_operation()
    log(f"✅ Operation successful: {result}", log_type='INFO')
    return True, result
except SpecificError as e:
    log(f"❌ Operation failed: {e}", log_type='ERROR')
    return False, str(e)
except Exception as e:
    log(f"❌ Unexpected error: {e}", log_type='ERROR', debug_only=False)
    return False, f"Unexpected error: {e}"
```

**Return Convention:** `(success: bool, message: str)` tuple for operations

### 3. **Logging Levels**

```python
# Log type hierarchy:
log("Message", log_type='DEBUG')    # Only shown with --debug
log("Message", log_type='INFO')     # Standard output
log("Message", log_type='WARNING')  # Potential issues
log("Message", log_type='ERROR')    # Failures
log("Message", log_type='SUCCESS')  # Completions

# Debug-only flag:
log("Detailed info", debug_only=True)  # Only with --debug flag
```

### 4. **Thread-Safe Data Access**

```python
class PathClassifier:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()  # Shared lock
    
    def classify_file(self, file):
        # ... classification logic ...
        
        # Thread-safe append:
        with self.lock:
            self.results.append(result)
```

**Pattern:** Always use `with self.lock:` for shared data structures.

### 5. **Rich vs. Fallback Pattern**

```python
# Check if Rich is available:
try:
    from rich.console import Console
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Use conditionally:
if RICH_AVAILABLE:
    console = Console()
    console.print("[green]Success![/green]")
else:
    print("Success!")  # Plain fallback
```

**Why:** Users without Rich still get functional (if less pretty) output.

### 6. **Path Handling**

```python
# Always use pathlib for new code:
from pathlib import Path

# Modern path handling:
source = Path(source_path)
files = list(source.glob("**/*.esp"))

# But use os.path for compatibility:
dest = os.path.join(base, relative)  # Cross-platform
```

### 7. **Comprehensive Logging Pattern**

```python
# ComprehensiveLogger usage (debug logging):
from comprehensive_logging import ComprehensiveLogger

class MyClass:
    def __init__(self):
        self.logger = ComprehensiveLogger('MyClass')
    
    def my_operation(self):
        # Start timing:
        timing_id = self.logger.start_timing('my_operation')
        
        # Log operation start:
        self.logger.log_operation_start('My Operation', {
            'param1': value1,
            'param2': value2
        })
        
        try:
            # ... do work ...
            
            # Log success:
            self.logger.log_operation_end('My Operation', True, {
                'result': result
            })
            self.logger.end_timing(timing_id, True)
            
        except Exception as e:
            # Log failure:
            self.logger.log_operation_end('My Operation', False, {
                'error': str(e)
            })
            self.logger.end_timing(timing_id, False)
            raise
```

### 8. **Temp Directory Management**

```python
# WRONG (don't use context manager for long-running):
with tempfile.TemporaryDirectory() as temp_dir:
    # ... long processing ...
    # Cleanup might fail if files locked

# RIGHT (manual cleanup with explicit delays):
temp_dir = tempfile.mkdtemp()
try:
    # ... processing ...
    time.sleep(2)  # Let processes release handles
finally:
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        log(f"Warning: Temp cleanup failed: {e}")
```

### 9. **Case-Insensitive Path Matching**

```python
# Game file systems are case-insensitive (Windows)
# But Python is case-sensitive, so:

def find_file_case_insensitive(root, rel_path):
    """Navigate path case-insensitively."""
    parts = rel_path.replace('\\', '/').split('/')
    current = root
    
    for part in parts:
        # List directory, match case-insensitively:
        match = next(
            (f for f in os.listdir(current) if f.lower() == part.lower()),
            None
        )
        if match:
            current = os.path.join(current, match)
        else:
            return None  # Path doesn't exist
    
    return current
```

**Used For:** Finding vanilla files in game Data folder

### 10. **Version Management (Single Source of Truth)**

```python
# Version defined ONLY in __init__.py:
# src/safe_resource_packer/__init__.py
__version__ = "1.1.3"

# setup.py parses it (no import):
def get_version():
    init_path = 'src/safe_resource_packer/__init__.py'
    with open(init_path, 'r') as f:
        content = f.read()
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
        if match:
            return match.group(1)

# build_release.py imports it (okay, not during packaging):
from safe_resource_packer import __version__
```

**Why:** Avoids version sync issues across multiple files.

---

## ⚠️ Known Issues & Quirks

### 1. **Windows Path Length Limit (260 characters)**

**Issue:** Windows has MAX_PATH = 260 character limit by default.

**Symptoms:**
- "Path too long" errors
- Files silently skipped
- Copy operations fail

**Workarounds in Code:**
```python
# 1. Validate path length before operations:
from .utils import validate_path_length

is_valid, error = validate_path_length(path)
if not is_valid:
    log(f"Path too long: {error}")
    return False

# 2. Use short temp directory names:
prefix = "7z_" if os.name == 'nt' else "7z_unified_"
temp_dir = tempfile.mkdtemp(prefix=prefix)
```

**User Solution:**
- Enable long paths in Windows Registry
- Extract to shorter path (e.g., `C:\SRP\`)

### 2. **Antivirus False Positives**

**Issue:** Tools like BSArch.exe, 7z.exe, and even the Python bundled release trigger antivirus warnings.

**Why:**
- Binary executables from downloads
- File system operations (read/write/hash)
- Subprocess execution

**User Solution:**
- Add folder to antivirus exclusions
- All tools are legitimate and open-source

### 3. **BSArch Windows-Only**

**Issue:** BSArch (optimal BSA/BA2 creation) only works on Windows.

**Code Handles This:**
```python
try:
    bsarch_path = find_bsarch()
    if bsarch_path:
        return create_with_bsarch(...)  # Optimal
except:
    pass

# Fallback to ZIP:
return create_with_zip(...)  # Works but not optimal
```

**Impact:** Linux/Mac users get ZIP fallback (works but larger files).

### 4. **7z Process Handle Lingering (Fixed in v1.1.3)**

**Issue:** On Windows, 7z.exe didn't always release file handles immediately after completion.

**Symptoms:**
- "File in use" errors
- Corrupted archives
- Access denied on cleanup

**Fix:**
```python
# Changed from subprocess.run (unreliable):
result = subprocess.run(['7z', ...])

# To Popen with explicit waits (reliable):
process = subprocess.Popen(['7z', ...])
stdout, stderr = process.communicate()
process.wait()  # Explicit termination
time.sleep(2)   # OS handle release
```

### 5. **Rich Library Version Detection**

**Issue:** Newer Rich versions don't expose `__version__` directly.

**Fixed in v1.1.3:**
```python
try:
    from rich import __version__ as rich_version
    print(f"Rich {rich_version}")
except ImportError:
    print("Rich (version unknown)")  # Fallback
```

### 6. **Recursion in User Profile Loading (Fixed in v1.1.2)**

**Issue:** Circular dependency caused infinite loop:
- `load_user_profile()` → `create_initial_profile()` → `detect_games()` → `load_user_profile()` → ...

**Fix:** Recursion guard pattern:
```python
class UserProfiler:
    def __init__(self):
        self._loading_profile = False
    
    def load_user_profile(self):
        if self._loading_profile:  # Guard check
            return {}
        
        self._loading_profile = True
        try:
            # ... actual loading
        finally:
            self._loading_profile = False  # Always reset
```

### 7. **Case Sensitivity Mismatch**

**Quirk:** Windows is case-insensitive, but Python is case-sensitive.

**Example:**
```
Vanilla: meshes/armor/iron/ironhelmet.nif
Mod:     Meshes/Armor/Iron/IronHelmet.nif
```

**Solution:** All path comparisons use `.lower()` normalization:
```python
# Find vanilla file:
vanilla_path = find_file_case_insensitive(source, rel_path)

def find_file_case_insensitive(root, path):
    # Compare everything in lowercase
    for part in path.split('/'):
        match = next((f for f in os.listdir(current) 
                     if f.lower() == part.lower()), None)
```

### 8. **Disk Space Calculation Over-Estimation**

**Quirk:** Disk space check is conservative, may show warning when space is actually sufficient.

**Why:**
- Accounts for compression overhead
- Assumes worst-case temp file expansion
- Better safe than crash mid-operation

**Formula:**
```python
required_space = (
    (generated_size * 3) +  # Source copy + Generated + Output
    (generated_size * 0.5)  # Compression overhead estimate
)
```

### 9. **ESP Templates Missing in Wheel (Fixed in v1.1.3)**

**Issue:** ESP template files weren't included in pip-installed packages.

**Symptom:** `FileNotFoundError: skyrim_template.esp`

**Fix:** Added to packaging config:
```python
# setup.py:
package_data={
    "safe_resource_packer": [
        "templates/esp/*.esp",
        "templates/esp/*.md",
    ],
}

# MANIFEST.in:
include src/safe_resource_packer/templates/esp/*.esp
include src/safe_resource_packer/templates/esp/*.md
```

### 10. **Game Detection Can Be Slow**

**Issue:** Full drive search for game installations can take 30-60 seconds.

**When It Happens:**
- First run (no profile)
- Games not in Steam/common paths
- Manual re-detection

**Solution:** Results are cached in user profile, only runs once unless manually triggered.

---

## ✅ Common Tasks

### Task 1: Add Support for New Game

```python
# 1. Add game to constants.py:
GAME_SPECIFIC_UNPACKABLE_FOLDERS = {
    'newgame': ['NGSE', 'NewGameMCM'],  # Script extenders, etc.
}

# 2. Update game_scanner.py:
def get_game_executables():
    return {
        'newgame': ['NewGame.exe', 'NewGameLauncher.exe']
    }

# 3. Update archive_creator.py:
def get_archive_extension(game_type):
    if game_type == 'newgame':
        return '.newarchive'  # Or .bsa/.ba2

# 4. Add ESP template:
# templates/esp/newgame_template.esp

# 5. Update CLI help:
@click.option('--game-type', 
              type=click.Choice(['skyrim', 'fallout4', 'newgame']))
```

### Task 2: Add New Blacklist Folder

```python
# Edit: src/safe_resource_packer/constants.py

UNPACKABLE_FOLDERS = {
    'Scripts',
    'SKSE',
    'MCM',
    'NewFolderToBlacklist',  # Add here (case-insensitive)
}

# Or game-specific:
GAME_SPECIFIC_UNPACKABLE_FOLDERS = {
    'skyrim': ['SKSE', 'SkyUI', 'NewSkyrimFolder'],
}
```

### Task 3: Update Version Number

```python
# 1. Update version (single source of truth):
# Edit: src/safe_resource_packer/__init__.py
__version__ = "1.2.0"  # Update here ONLY

# 2. Update changelog:
# Edit: CHANGELOG.md
## [1.2.0] - 2025-XX-XX
### New Features
- ...

# 3. Update pyproject.toml (manual):
# Edit: pyproject.toml
version = "1.2.0"

# setup.py and build_release.py auto-read from __init__.py
```

### Task 4: Build Bundled Release

```bash
# 1. Ensure version is correct in __init__.py

# 2. Run build script:
python build_release.py

# 3. Output will be in release/:
release/
└── safe-resource-packer-X.X.X-bundled.zip
    ├── python/                    # Complete Python environment
    ├── run_safe_resource_packer.bat
    └── README.txt

# 4. Test the release:
cd release/safe-resource-packer-X.X.X-bundled/
.\run_safe_resource_packer.bat
```

### Task 5: Debug Classification Issues

```python
# 1. Run with debug logging:
safe-resource-packer --source ./Data --generated ./Output \
                     --package ./MyMod --mod-name "TestMod" \
                     --debug

# 2. Check debug log file:
# Location: ./safe_resource_packer_debug.log

# 3. Look for classification entries:
grep "Classified:" safe_resource_packer_debug.log

# 4. Check SHA1 hashes:
grep "SHA1:" safe_resource_packer_debug.log

# 5. Verify case-insensitive matching:
grep "Case-insensitive match" safe_resource_packer_debug.log
```

### Task 6: Add New CLI Option

```python
# Edit: src/safe_resource_packer/enhanced_cli.py

@click.command()
@click.option('--my-option', 
              type=str,
              default='default_value',
              help='Description of my option')
def enhanced_main(my_option, ...):
    """CLI function."""
    
    # Use the option:
    if my_option:
        # ... logic
    
    # Pass to core:
    packer = SafeResourcePacker(my_option=my_option)
```

### Task 7: Fix Corrupted Archive Issue

```python
# 1. Check if archive integrity test is running:
# Look in code: package_builder.py → _test_archive_integrity()

# 2. Increase wait times if needed:
# Edit: compression_service.py
time.sleep(3)  # Increase from 2 to 3

# 3. Add more aggressive file flush:
# Edit: package_builder.py → After compression
with open(archive_path, 'rb') as f:
    f.read()  # Force full read
    f.flush()
    os.fsync(f.fileno())  # Force OS flush

# 4. Test with large files:
# Use ~1GB+ test mod to reproduce issue
```

### Task 8: Add Interactive Tutorial Step

```python
# Edit: src/safe_resource_packer/tutorials/interactive_tutorial.py

def new_tutorial_step(self):
    """Add new tutorial section."""
    self.console.print(Panel(
        "[bold cyan]New Tutorial Step[/bold cyan]\n\n"
        "Explanation here...",
        title="Step X",
        border_style="cyan"
    ))
    
    # Show example:
    self._show_example_code()
    
    # Quiz:
    answer = self._ask_quiz_question(
        "Question here?",
        ["Option A", "Option B"],
        correct=0
    )
    
    return answer

# Add to tutorial flow:
def run_tutorial(self):
    # ...
    self.new_tutorial_step()  # Add here
```

### Task 9: Profile Performance Bottleneck

```python
# 1. Enable comprehensive logging:
from comprehensive_logging import ComprehensiveLogger

logger = ComprehensiveLogger('MyModule')

# 2. Add timing around suspected code:
timing_id = logger.start_timing('my_operation')
# ... code to profile ...
logger.end_timing(timing_id, success=True)

# 3. Check debug log for timing stats:
grep "TIMING:" safe_resource_packer_debug.log

# 4. For detailed profiling, use cProfile:
python -m cProfile -s cumtime -m safe_resource_packer \
    --source ./Data --generated ./Output \
    --package ./Output --mod-name "Profile"
```

### Task 10: Test with Different Game Types

```bash
# Skyrim SE:
safe-resource-packer --game-type skyrim \
    --source "C:/SkyrimSE/Data" \
    --generated "./MySkyrimMod" \
    --package "./Output" \
    --mod-name "SkyrimTest"

# Skyrim VR:
safe-resource-packer --game-type skyrimvr \
    --source "C:/SkyrimVR/Data" \
    --generated "./MyVRMod" \
    --package "./Output" \
    --mod-name "VRTest"

# Fallout 4:
safe-resource-packer --game-type fallout4 \
    --source "C:/Fallout4/Data" \
    --generated "./MyF4Mod" \
    --package "./Output" \
    --mod-name "Fallout4Test"

# Fallout 4 VR:
safe-resource-packer --game-type fallout4vr \
    --source "C:/Fallout4VR/Data" \
    --generated "./MyF4VRMod" \
    --package "./Output" \
    --mod-name "F4VRTest"
```

---

## 🧪 Testing

### Manual Testing Checklist:

**1. Intelligent Packer (Single Mod):**
```bash
# Test with small dataset:
safe-resource-packer \
    --source "./test_data/SkyrimData" \
    --generated "./test_data/TestMod" \
    --package "./test_output" \
    --mod-name "TestMod" \
    --game-type skyrim \
    --debug

# Verify output:
test_output/
├── TestMod_v1.0.7z          # Should contain BSA + ESP
└── TestMod_Loose.7z          # Should contain modified files (if any)

# Test archive integrity:
7z t test_output/TestMod_v1.0.7z
```

**2. Batch Repacker:**
```bash
# Prepare test collection:
test_collection/
├── ModA/
│   ├── ModA.esp
│   └── meshes/
├── ModB/
│   ├── ModB.esm
│   └── textures/
└── ModC/
    ├── ModC.esl
    └── sounds/

# Run batch repacker via UI:
safe-resource-packer-ui
# Select: 2. Batch Mod Repacking
# Point to test_collection/
```

**3. Game Detection:**
```bash
# Test game detection:
python -c "
from safe_resource_packer.onboarding.user_profiler import UserProfiler
profiler = UserProfiler()
profiler.detect_games()
print(profiler.detected_games)
"
```

**4. Archive Integrity (Critical):**
```bash
# Create large test mod (~1GB+)
# Run intelligent packer
# Check for corruption:

7z t output/ModName_v1.0.7z
# Should show: "Everything is Ok"

# Try to extract:
7z x output/ModName_v1.0.7z -o./test_extract/
# Should extract without errors
```

### Automated Tests:

```bash
# Run pytest tests:
python -m pytest tests/ -v

# Run specific test:
python -m pytest tests/test_classifier.py -v

# Run with coverage:
python -m pytest tests/ --cov=safe_resource_packer --cov-report=html
```

### Test Files Structure:

```
tests/
├── test_core.py              # SafeResourcePacker tests
├── test_classifier.py        # PathClassifier tests
├── test_utils.py             # Utility function tests
├── test_archive_creator.py   # Archive creation tests
└── fixtures/
    ├── sample_esp.esp
    ├── test_files/
    └── mock_data/
```

### Writing New Tests:

```python
# tests/test_my_feature.py

import pytest
from safe_resource_packer.my_module import MyClass

class TestMyFeature:
    @pytest.fixture
    def setup(self):
        """Setup test environment."""
        # ... setup code
        yield my_instance
        # ... teardown code
    
    def test_my_function(self, setup):
        """Test my function."""
        result = setup.my_function(input_data)
        assert result == expected_output
    
    def test_error_handling(self, setup):
        """Test error handling."""
        with pytest.raises(MyException):
            setup.my_function(bad_input)
```

---

## 🔧 Troubleshooting

### Issue 1: "No module named safe_resource_packer"

**Symptom:**
```
ModuleNotFoundError: No module named 'safe_resource_packer'
```

**Causes & Solutions:**

1. **Not installed:**
```bash
pip install -e .  # Development install
# OR
pip install safe-resource-packer  # PyPI install
```

2. **Wrong Python environment:**
```bash
# Check which Python:
which python  # Linux/Mac
where python  # Windows

# Activate correct venv:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Bundled release issue:**
```bash
# Bundled release should include package
# If missing, rebuild:
python build_release.py
```

### Issue 2: "Path too long" errors

**Symptom:**
```
Error: Path exceeds maximum length (260 characters)
[PATH TOO LONG] meshes/armor/...
```

**Solutions:**

1. **Extract to shorter path:**
```bash
# Instead of:
C:\Users\Username\Documents\Projects\Modding\TestProject\

# Use:
C:\SRP\
```

2. **Enable long paths (Windows):**
```powershell
# Run as Administrator:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
-Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

3. **Use shorter mod names:**
```bash
# Instead of:
--mod-name "MyAwesomeModWithVeryLongNameThatExceedsLimits"

# Use:
--mod-name "MyMod"
```

### Issue 3: Corrupted 7z archive

**Symptom:**
```
Error: Catastrophic failure when opening archive
7z test shows: CRC failed
```

**Solutions (v1.1.3+):**

1. **Verify fix is applied:**
```python
# Check: compression_service.py
# Should use: subprocess.Popen + process.wait() + time.sleep(2)
# NOT: subprocess.run()
```

2. **Increase wait times:**
```python
# Edit: compression_service.py
time.sleep(3)  # Increase from 2
```

3. **Check disk space:**
```bash
# Ensure enough space for:
# - Source files
# - Temp files (3x source size)
# - Output archives
```

4. **Test archive immediately:**
```bash
7z t -slt output/ModName_v1.0.7z
# Should show: "Everything is Ok"
```

### Issue 4: BSArch not found

**Symptom:**
```
Warning: BSArch not found, using ZIP fallback
Archives will be larger and not optimal
```

**Solutions:**

1. **Auto-install BSArch:**
```bash
safe-resource-packer --install-bsarch
```

2. **Manual download:**
- Download from: https://www.nexusmods.com/fallout4/mods/
- Place `BSArch.exe` in one of:
  - `./BSArch/BSArch.exe`
  - `C:\Program Files\BSArch\BSArch.exe`
  - Add to PATH

3. **Verify detection:**
```python
python -c "
from safe_resource_packer.bsarch_service import find_bsarch
print(find_bsarch())
"
```

### Issue 5: Game not detected

**Symptom:**
```
No games detected
Please manually specify --game-path
```

**Solutions:**

1. **Manual game path:**
```bash
safe-resource-packer --game-path "C:/SkyrimSE/Data" ...
```

2. **Re-detect games:**
```bash
# Via UI:
safe-resource-packer-ui
# → Tools & System → Re-detect Game Installations

# Via profile deletion:
rm ~/.safe_resource_packer_profile.json  # Linux/Mac
del %USERPROFILE%\.safe_resource_packer_profile.json  # Windows
```

3. **Check expected locations:**
```
# Steam default:
C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition\Data

# Vortex:
Check: %APPDATA%\Vortex\settings.json
```

### Issue 6: Antivirus blocking

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
File was deleted by antivirus
```

**Solutions:**

1. **Add exclusion:**
```
Windows Defender:
Settings → Virus & threat protection
→ Manage settings → Add exclusion
→ Folder → Select project folder
```

2. **Whitelist files:**
- `BSArch.exe`
- `7z.exe`
- `run_safe_resource_packer.bat`
- Entire bundled release folder

3. **Verify files:**
```bash
# Check SHA256 hashes match official releases
certutil -hashfile BSArch.exe SHA256  # Windows
shasum -a 256 BSArch.exe              # Linux/Mac
```

### Issue 7: High memory usage

**Symptom:**
```
Process using 4GB+ RAM
System slows down during processing
```

**Solutions:**

1. **Reduce thread count:**
```bash
safe-resource-packer --threads 4 ...  # Instead of default 8
```

2. **Process in batches:**
```bash
# Split large mod into smaller folders
# Process each separately
```

3. **Monitor usage:**
```python
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```

### Issue 8: Classification taking too long

**Symptom:**
```
SHA1 hashing stuck at 50% for 10+ minutes
```

**Causes:**

1. **Large files (4K textures):** Normal, be patient
2. **Too many threads:** Reduce with `--threads`
3. **Slow disk (HDD):** Use SSD if possible
4. **Antivirus scanning:** Add exclusion

**Performance expectations:**
- 1000 files: ~1-2 minutes
- 10,000 files: ~10-20 minutes
- 100,000 files: ~1-2 hours

### Issue 9: ESP doesn't load archive

**Symptom:**
```
ESP is active in load order
Archive exists in Data folder
But assets don't appear in-game
```

**Solutions:**

1. **Check name matching:**
```
❌ WRONG:
MyMod.esp
MyModArchive.bsa

✅ CORRECT:
MyMod.esp
MyMod.bsa  # Must match ESP base name
```

2. **Check archive flag in ESP:**
```python
# ESP must have archive flag set
# Tool does this automatically
# Verify with xEdit or Creation Kit
```

3. **Check load order:**
```
# ESP must be active (checked)
# Not just present in Data folder
```

### Issue 10: Rich formatting not showing

**Symptom:**
```
Output shows raw markup instead of colors:
[green]Success![/green] instead of colored "Success!"
```

**Solutions:**

1. **Check Rich installation:**
```bash
python -c "import rich; print(rich.__version__)"
# If error: pip install rich>=13.0.0
```

2. **Terminal doesn't support ANSI:**
```bash
# Windows: Use Windows Terminal, not cmd.exe
# Linux: Most terminals support it
# Mac: Terminal.app supports it
```

3. **Force fallback mode:**
```python
# Tool automatically falls back to plain text if Rich unavailable
# This is normal behavior
```

---

## 📦 Build & Release

### Build Workflow:

```
1. Update Version
   └── Edit: src/safe_resource_packer/__init__.py
       __version__ = "X.X.X"

2. Update Changelog
   └── Edit: CHANGELOG.md
       Add new version entry

3. Update pyproject.toml
   └── Edit: pyproject.toml
       version = "X.X.X"

4. Run Build Script
   └── python build_release.py
       ├── Cleans build directories
       ├── Builds wheel (.whl)
       ├── Builds source distribution (.tar.gz)
       ├── Creates bundled release (with Python)
       └── Generates release_info.json

5. Test Bundled Release
   └── cd release/safe-resource-packer-X.X.X-bundled/
       .\run_safe_resource_packer.bat
       Test all features

6. Create GitHub Release
   └── Tag: vX.X.X
       Upload: safe-resource-packer-X.X.X-bundled.zip

7. (Optional) Publish to PyPI
   └── twine upload dist/*
```

### Build Script Deep Dive:

**`build_release.py` does:**

1. **Version extraction:**
```python
# Parses version from __init__.py without importing
# Avoids dependency issues during build
import re
with open('src/safe_resource_packer/__init__.py') as f:
    version = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read()).group(1)
```

2. **Wheel building:**
```bash
python -m build --wheel
# Creates: dist/safe_resource_packer-X.X.X-py3-none-any.whl
```

3. **Bundled release creation:**
```python
# Copies entire Python installation
shutil.copytree(sys.prefix, bundled_dir / 'python')

# Installs dependencies in bundled Python
subprocess.run([bundled_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# Installs package itself
subprocess.run([bundled_python, '-m', 'pip', 'install', '.'])
```

4. **Launcher script:**
```batch
@echo off
:: Auto-detects bundled Python
:: Falls back to system Python
:: Launches safe-resource-packer
```

5. **Release packaging:**
```python
# Creates 7z archive
shutil.make_archive(
    release_dir / f'{PROJECT_NAME}-{VERSION}-bundled',
    'zip',
    bundled_dir
)
```

### Release Variants (Historical):

**Current (v1.1.0+):** Only bundled release

**Deprecated:**
- ~~Portable release~~ (removed in v1.1.0)
- ~~Source release~~ (available on GitHub)

### Release Checklist:

- [ ] Version updated in `__init__.py`
- [ ] Version updated in `pyproject.toml`
- [ ] Changelog updated with new version
- [ ] All tests passing
- [ ] Build script runs without errors
- [ ] Bundled release tested on clean Windows machine
- [ ] All features work in bundled release
- [ ] Documentation reflects version changes
- [ ] GitHub release created with tag
- [ ] Release notes written
- [ ] Nexus Mods page updated (if applicable)

### Versioning Scheme:

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes, major rewrites
- **MINOR:** New features, non-breaking changes
- **PATCH:** Bug fixes, small improvements

**Examples:**
- `1.0.0` → Initial stable release
- `1.1.0` → Added VR support (new feature)
- `1.1.1` → Fixed corruption bug (patch)
- `2.0.0` → Complete rewrite (breaking change)

### Distribution:

**GitHub Releases:**
- Primary distribution method
- `safe-resource-packer-X.X.X-bundled.zip`
- Full changelog in release notes

**PyPI (Optional):**
```bash
# Build
python -m build

# Upload
twine upload dist/*
```

**Nexus Mods (Optional):**
- Upload bundled ZIP
- Use prepared description from `docs/NEXUS_DESCRIPTION_BBCODE.txt`
- Add screenshots, usage examples

---

## 🎯 Project Philosophy

### Design Principles:

1. **Safety First:** Never modify original files, always work on copies
2. **Correctness Over Speed:** Proper archives > fast but wrong archives
3. **User-Friendly:** Works for beginners, powerful for experts
4. **Cross-Platform:** Python + external tools work everywhere
5. **Transparent:** Clear progress, helpful errors, debug logging
6. **Maintainable:** Clean code, consistent patterns, good docs

### Target Audience:

- **Primary:** Mod authors who use BodySlide or texture tools
- **Secondary:** Mod collection curators, power users
- **Skill Level:** Beginner-friendly UI, expert-friendly CLI

### Future Directions:

**Potential Features:**
- [ ] GUI (Tkinter/Qt) for even easier use
- [ ] Nexus Mods API integration (auto-upload)
- [ ] Config file support for batch operations
- [ ] Mod validation (check for common issues)
- [ ] Performance profiling mode
- [ ] Steam Workshop support (if applicable)

**No Plans For:**
- ❌ Non-Bethesda games (out of scope)
- ❌ Mod management features (use MO2/Vortex)
- ❌ In-game functionality (separate from modding tools)

---

## 📚 Additional Resources

### Internal Documentation:

- `docs/Getting_Started.md` - Quick start guide
- `docs/CLI_Reference.md` - Complete CLI reference
- `docs/API.md` - Python API documentation
- `docs/Packaging_Guide.md` - Deep dive into packaging
- `docs/Troubleshooting.md` - Common issues and solutions

### External Resources:

- **BSArch Documentation:** https://www.nexusmods.com/fallout4/mods/
- **7-Zip CLI Reference:** https://sevenzip.osdn.jp/chm/cmdline/index.htm
- **Creation Kit Wiki:** https://www.creationkit.com/
- **xEdit Documentation:** https://tes5edit.github.io/docs/

### Community:

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions and community help
- **Nexus Mods Forum:** User discussions and feedback

---

**Last Updated:** 2025-11-27  
**Document Version:** 1.0  
**Project Version:** 1.1.3

*This document should be updated whenever significant architectural changes, new features, or important patterns are introduced.*

