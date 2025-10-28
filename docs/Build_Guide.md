# 🚀 Safe Resource Packer - Build System

This document describes the build system for creating release packages - our equivalent of `npm run build`.

## 📋 Quick Start

### Windows (Easiest)
```bash
# One-click build - creates everything
build.bat

# Or using Python directly
python build_release.py
```

### Cross-Platform
```bash
# Unix/Linux/macOS
./build.sh

# Or using the script runner
python run_script.py build
```

## 📦 What Gets Built

The build system creates a complete release package with:

### 🎯 Distribution Files (`dist/`)
- **`safe_resource_packer-1.0.0-py3-none-any.whl`** - Python wheel for pip installation
- **`safe_resource_packer-1.0.0.tar.gz`** - Source distribution for PyPI

### 🚀 Release Files (`release/`)
- **`safe-resource-packer-1.0.0-bundled.zip`** - Self-contained package with complete Python environment (no installation required)
- **`release_info.json`** - Build metadata and file information

## 🔧 Available Scripts (npm-style)

We provide an `npm run` equivalent with `python run_script.py <script>`:

### Build Scripts
```bash
python run_script.py build          # Complete release build
python run_script.py build:quick    # Quick Python package build only
python run_script.py build:bundled  # Create bundled release with dependencies
python run_script.py build:clean    # Clean all build directories
```

### Development Scripts
```bash
python run_script.py install        # Install in development mode
python run_script.py install:deps   # Install dependencies only
python run_script.py run            # Launch UI
python run_script.py run:cli        # Launch CLI
python run_script.py dev            # Launch development version
```

### Testing Scripts
```bash
python run_script.py test           # Run full test suite
python run_script.py test:quick     # Run tests with fail-fast
```

### Release Scripts
```bash
python run_script.py release:test   # Validate distribution files
python run_script.py release:upload # Upload to PyPI
```

### List All Scripts
```bash
python run_script.py --list         # Show all available scripts
```

## 🎯 Build Process Details

The build system automatically:

1. **🧹 Cleans** old build artifacts
2. **🔍 Checks** and installs build dependencies (`build`, `twine`, `wheel`)
3. **🧪 Runs** the test suite (continues on failure)
4. **📦 Builds** Python wheel and source distributions
5. **🚀 Creates** bundled release with complete Python environment
6. **📋 Generates** release metadata

## 📁 Release Type: Bundled Only

### 📦 Bundled Release (`*-bundled.zip`)
**The ONLY distribution method - works for everyone!**

**Why bundled-only approach:**
- ✅ **Zero dependencies** - No Python installation required
- ✅ **True portability** - Works on any Windows machine
- ✅ **No path issues** - Self-contained Python environment
- ✅ **Consistent experience** - Same for all users
- ✅ **One-click setup** - Just extract and run

**What's included:**
- Complete Python installation (not venv!)
- All project dependencies pre-installed
- Batch launcher for instant use
- Full source code and examples
- Documentation

```
safe-resource-packer-1.0.0-bundled/
├── run_safe_resource_packer.bat    # One-click launcher
├── python/                         # Complete Python installation
│   ├── python.exe                 # Bundled Python interpreter
│   ├── Scripts/                   # Python scripts
│   └── Lib/site-packages/         # All dependencies installed
├── src/                            # Full source code
├── examples/                       # Usage examples
├── README.md & LICENSE            # Documentation
└── requirements.txt               # Dependency list (reference)
```

**Technical Details:**
- Uses full Python installation copy (not virtual environment)
- All paths are relative to the bundled directory
- No hardcoded paths - truly portable across machines
- Python and all dependencies are self-contained

## 🎯 Usage Examples

### For Development
```bash
# Clean build from scratch
python run_script.py build:clean
python run_script.py build

# Quick iteration
python run_script.py build:quick
python run_script.py test
```

### For Release
```bash
# Create complete release package
build.bat

# Validate the package
python run_script.py release:test

# Upload to PyPI (optional)
python run_script.py release:upload
```

### For Testing
```bash
# Extract and test portable ZIP on fresh PC
# Double-click run_safe_resource_packer.bat
```

## 🔧 Build Configuration

Build settings are in:
- **`build_release.py`** - Main build script
- **`scripts.json`** - npm-style script definitions  
- **`pyproject.toml`** - Python package metadata
- **`setup.py`** - Alternative package configuration

## 🎉 Output Summary

After a successful build:

```
📦 Distribution files (dist/):
   - safe_resource_packer-1.0.0-py3-none-any.whl (155,338 bytes)
   - safe_resource_packer-1.0.0.tar.gz (149,456 bytes)

🚀 Release files (release/):
   - safe-resource-packer-1.0.0-portable.zip (524,601 bytes)
   - safe-resource-packer-1.0.0-source.zip (350,696 bytes)

🎯 Ready for:
   - PyPI upload: twine upload dist/*
   - GitHub release: Upload files from release/
   - Local testing: Use portable ZIP
```

## 🚨 Troubleshooting

### Common Issues
- **Build fails**: Check Python and pip are up to date
- **Missing dependencies**: Run `python run_script.py install:deps`
- **Test failures**: Build continues anyway, but fix tests for production
- **Permission errors**: Run as administrator on Windows

### Clean Start
```bash
python run_script.py build:clean
python run_script.py install:deps
python run_script.py build
```

---

**🎯 The build system provides everything needed for professional releases - from development to distribution!**
