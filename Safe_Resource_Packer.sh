#!/bin/bash
# Safe Resource Packer - Enhanced Unix Launcher
# For Linux and macOS systems

set -e

echo ""
echo "================================================================================"
echo "                        🚀 SAFE RESOURCE PACKER 🚀"
echo "                     Enhanced Auto-Installing Launcher"
echo "================================================================================"
echo ""
echo "This launcher automatically handles all dependencies and setup!"
echo ""
echo "💡 What this tool does:"
echo "   • Classifies your mod files intelligently"
echo "   • Creates professional mod packages (BSA/BA2 + ESP)"
echo "   • Optimizes for game performance"
echo "   • Works with BodySlide, Outfit Studio, and other tools"
echo ""
echo "🎮 Perfect for: Skyrim, Fallout 4, and other Creation Engine games"
echo ""
echo "🔧 Auto-Setup Features:"
echo "   • Checks and installs Python if needed"
echo "   • Upgrades pip for better compatibility"
echo "   • Installs all required dependencies"
echo "   • Auto-installs 7z for optimal compression"
echo "   • Handles virtual environments intelligently"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="Unknown:${OS}"
esac

echo "🖥️  Detected OS: $MACHINE"

# Check Python
echo "🔍 Checking Python installation..."
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo "✅ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" &> /dev/null; then
        PYTHON="python"
        echo "✅ Python found: $(python --version)"
    else
        echo "❌ Python version is too old (need 3.7+)"
        PYTHON=""
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "❌ ERROR: Python 3.7+ is not installed or not in PATH"
    echo ""
    echo "📥 PYTHON INSTALLATION REQUIRED"
    echo ""
    case "$MACHINE" in
        Linux)
            echo "For Ubuntu/Debian:"
            echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
            echo ""
            echo "For Arch Linux:"
            echo "   sudo pacman -S python python-pip"
            echo ""
            echo "For CentOS/RHEL/Fedora:"
            echo "   sudo dnf install python3 python3-pip"
            ;;
        Mac)
            echo "For macOS:"
            echo "   brew install python3"
            echo "   or download from: https://www.python.org/downloads/"
            ;;
        *)
            echo "Please install Python 3.7+ for your system"
            ;;
    esac
    echo ""
    exit 1
fi

# Check and install 7z for optimal compression performance
echo "🗜️  Checking 7z installation..."
SEVENZ_FOUND=""

# Check common 7z command variants
if command -v 7z &> /dev/null; then
    SEVENZ_FOUND="7z"
    echo "✅ 7z found in PATH"
elif command -v 7za &> /dev/null; then
    SEVENZ_FOUND="7za"
    echo "✅ 7za (7-Zip standalone) found in PATH"
elif command -v 7zr &> /dev/null; then
    SEVENZ_FOUND="7zr"
    echo "✅ 7zr (7-Zip reduced) found in PATH"
else
    # Check common installation paths
    COMMON_PATHS=("/usr/bin/7z" "/usr/local/bin/7z" "/opt/7z/7z")
    for path in "${COMMON_PATHS[@]}"; do
        if [ -f "$path" ]; then
            SEVENZ_FOUND="$path"
            echo "✅ 7z found: $path"
            break
        fi
    done
fi

if [ -z "$SEVENZ_FOUND" ]; then
    echo "❌ 7z not found - installing for optimal compression performance..."
    echo ""
    echo "🚀 AUTOMATIC 7Z INSTALLATION"
    echo ""
    echo "7z provides much faster multithreaded compression than built-in tools."
    echo "This significantly improves mod packaging speed!"
    echo ""
    
    case "$MACHINE" in
        Linux)
            # Detect Linux distribution
            if command -v apt &> /dev/null; then
                echo "🐧 Using APT to install p7zip-full..."
                if sudo apt update && sudo apt install -y p7zip-full; then
                    echo "✅ 7z installed successfully via APT!"
                    SEVENZ_FOUND="7z"
                else
                    echo "⚠️  APT install failed"
                fi
            elif command -v pacman &> /dev/null; then
                echo "🏹 Using Pacman to install p7zip..."
                if sudo pacman -S --noconfirm p7zip; then
                    echo "✅ 7z installed successfully via Pacman!"
                    SEVENZ_FOUND="7z"
                else
                    echo "⚠️  Pacman install failed"
                fi
            elif command -v dnf &> /dev/null; then
                echo "🎩 Using DNF to install p7zip..."
                if sudo dnf install -y p7zip p7zip-plugins; then
                    echo "✅ 7z installed successfully via DNF!"
                    SEVENZ_FOUND="7z"
                else
                    echo "⚠️  DNF install failed"
                fi
            elif command -v yum &> /dev/null; then
                echo "🎩 Using YUM to install p7zip..."
                if sudo yum install -y p7zip p7zip-plugins; then
                    echo "✅ 7z installed successfully via YUM!"
                    SEVENZ_FOUND="7z"
                else
                    echo "⚠️  YUM install failed"
                fi
            else
                echo "💡 Unknown Linux distribution - please install p7zip manually:"
                echo "   Ubuntu/Debian: sudo apt install p7zip-full"
                echo "   Arch: sudo pacman -S p7zip"
                echo "   Fedora/CentOS: sudo dnf install p7zip p7zip-plugins"
            fi
            ;;
        Mac)
            # Try Homebrew first
            if command -v brew &> /dev/null; then
                echo "🍺 Using Homebrew to install p7zip..."
                if brew install p7zip; then
                    echo "✅ 7z installed successfully via Homebrew!"
                    SEVENZ_FOUND="7z"
                else
                    echo "⚠️  Homebrew install failed"
                fi
            else
                echo "💡 Homebrew not found. Please install 7z manually:"
                echo "   1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo "   2. Install p7zip: brew install p7zip"
                echo "   Or download from: https://www.7-zip.org/"
            fi
            ;;
        *)
            echo "💡 Unknown system - please install p7zip/7z manually"
            ;;
    esac
    
    if [ -z "$SEVENZ_FOUND" ]; then
        echo "⚠️  Automatic 7z installation failed"
        echo "💡 Please install 7z manually for optimal performance:"
        echo "   The tool will work without it, but compression will be slower"
    fi
    echo ""
else
    echo "✅ 7z is ready for optimal compression performance!"
fi

# Check and upgrade pip
echo "📦 Ensuring pip is up to date..."
$PYTHON -m pip install --upgrade pip --quiet --user
if [ $? -ne 0 ]; then
    echo "⚠️  Could not upgrade pip (continuing anyway...)"
fi

# Check if we're in a development directory
DEV_MODE=""
if [ -d "src/safe_resource_packer" ]; then
    DEV_MODE="1"
    echo "🛠️  Development mode detected (found src/ folder)"
fi

# Install/check dependencies
if [ -n "$DEV_MODE" ]; then
    echo "📥 Installing in development mode..."
    $PYTHON -m pip install -e . --quiet --user
    if [ $? -ne 0 ]; then
        echo "⚠️  Development install failed, trying requirements.txt..."
        if [ -f "requirements.txt" ]; then
            $PYTHON -m pip install -r requirements.txt --quiet --user
        fi
    fi
else
    # Check if safe-resource-packer is installed
    if ! $PYTHON -c "import safe_resource_packer" &> /dev/null; then
        echo "❌ Safe Resource Packer is not installed"
        echo ""
        echo "📥 Installing Safe Resource Packer and dependencies..."
        echo "   This may take a few minutes on first run..."
        echo ""
        
        # Try to install from PyPI first
        $PYTHON -m pip install safe-resource-packer --quiet --user
        if [ $? -ne 0 ]; then
            echo "⚠️  PyPI install failed, trying local requirements..."
            if [ -f "requirements.txt" ]; then
                echo "📋 Installing from requirements.txt..."
                $PYTHON -m pip install -r requirements.txt --quiet --user
            fi
            if [ -f "setup.py" ]; then
                echo "🔧 Installing from setup.py..."
                $PYTHON -m pip install . --quiet --user
            fi
        fi
        
        # Final check
        if ! $PYTHON -c "import safe_resource_packer" &> /dev/null; then
            echo "❌ Installation failed. Trying alternative methods..."
            echo ""
            echo "🌐 Checking internet connection..."
            if ping -c 1 google.com &> /dev/null; then
                echo "✅ Internet connection OK"
                echo "🔄 Trying manual dependency installation..."
                $PYTHON -m pip install rich click colorama py7zr --quiet --user
                if [ -d "src/safe_resource_packer" ]; then
                    echo "📁 Installing from local source..."
                    $PYTHON -m pip install -e . --quiet --user
                fi
            else
                echo "❌ No internet connection detected"
                echo "💡 Please connect to internet and try again"
                exit 1
            fi
        else
            echo "✅ Installation complete!"
        fi
        echo ""
    else
        echo "✅ Safe Resource Packer is already installed"
        
        # Check if we need to update dependencies
        if ! $PYTHON -c "import rich, click, colorama, py7zr" &> /dev/null; then
            echo "📦 Installing missing dependencies..."
            $PYTHON -m pip install rich click colorama py7zr --quiet --user
        fi
    fi
fi

# Final status check and launch
if $PYTHON -c "import safe_resource_packer; print('✅ All systems ready!')" 2>/dev/null; then
    echo "✅ Dependencies installed and verified!"
else
    echo ""
    echo "⚠️  WARNING: There may be issues with the installation"
    echo "🛠️  RECOVERY OPTIONS:"
    echo ""
    echo "1. Try running with sudo (if permissions issue)"
    echo "2. Check firewall settings"
    echo "3. Restart this launcher"
    echo "4. Manual installation: $PYTHON -m pip install safe-resource-packer --user"
    echo ""
    echo "💡 You can still try to continue, but some features may not work"
    echo ""
    read -p "Continue anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Launching Safe Resource Packer..."
echo "   All menus and options are handled by the Python interface"
echo "   No command-line knowledge required!"
echo ""
read -p "Press Enter to continue..."

# Launch the Python script - try different methods in order of preference
echo "🔄 Launching via Python module..."
if $PYTHON -m safe_resource_packer; then
    echo ""
    echo "✅ Safe Resource Packer session completed"
    echo ""
    echo "💡 TIP: You can run this .sh file anytime to launch the tool"
    echo "   All your Python dependencies will be automatically managed!"
    echo ""
    exit 0
fi

# Method 2: Try the console script entry point
echo "🔄 Trying console script entry point..."
if safe-resource-packer; then
    exit 0
fi

# Method 3: Development mode - direct script execution
if [ -n "$DEV_MODE" ]; then
    echo "🔄 Development mode - trying direct script execution..."
    if $PYTHON src/safe_resource_packer/console_ui.py; then
        exit 0
    fi
    
    if $PYTHON src/safe_resource_packer/enhanced_cli.py; then
        exit 0
    fi
fi

# Method 4: Import and run directly
echo "🔄 Trying direct import method..."
if $PYTHON -c "from safe_resource_packer.console_ui import run_console_ui; from safe_resource_packer.enhanced_cli import execute_with_config; config = run_console_ui(); exit(0 if not config else execute_with_config(config))"; then
    exit 0
fi

# If all else fails, show error
echo ""
echo "❌ Could not launch Safe Resource Packer"
echo ""
echo "🛠️  TROUBLESHOOTING:"
echo ""
echo "1. Try running: safe-resource-packer"
echo "2. Or try: $PYTHON -m safe_resource_packer"
echo "3. Check installation: $PYTHON -m pip list | grep safe-resource-packer"
echo "4. Reinstall: $PYTHON -m pip install --force-reinstall safe-resource-packer --user"
echo ""
exit 1
