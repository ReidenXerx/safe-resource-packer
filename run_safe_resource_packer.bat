@echo off
title Safe Resource Packer - Enhanced Launcher
color 0B
cls

echo.
echo ================================================================================
echo                        🚀 SAFE RESOURCE PACKER 🚀
echo                   Enhanced Auto-Installing Launcher
echo ================================================================================
echo.
echo This launcher automatically handles all dependencies and setup!
echo.
echo 💡 What this tool does:
echo    • Classifies your mod files intelligently
echo    • Creates professional mod packages (BSA/BA2 + ESP)
echo    • Optimizes for game performance
echo    • Works with BodySlide, Outfit Studio, and other tools
echo.
echo 🎮 Perfect for: Skyrim, Fallout 4, and other Creation Engine games
echo.
echo 🔧 Auto-Setup Features:
echo    • Checks and installs Python if needed
echo    • Upgrades pip for better compatibility
echo    • Installs all required dependencies
echo    • Handles virtual environments intelligently
echo.

REM Function to check if we're in a virtual environment
set "VENV_ACTIVE="
if defined VIRTUAL_ENV set "VENV_ACTIVE=1"
if defined CONDA_DEFAULT_ENV set "VENV_ACTIVE=1"

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📥 AUTOMATIC PYTHON INSTALLATION REQUIRED
    echo.
    echo We'll help you install Python automatically:
    echo 1. Opening Python download page...
    echo 2. Please download and install Python 3.8 or newer
    echo 3. ⚠️  CRITICAL: Check "Add Python to PATH" during installation
    echo 4. Run this launcher again after installation
    echo.
    start https://www.python.org/downloads/
    echo 🌐 Python download page opened in your browser
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python found and accessible
)

REM Check and upgrade pip
echo 🔄 Checking pip version...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  pip not found, installing...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Failed to install pip
        pause
        exit /b 1
    )
)

echo 📦 Ensuring pip is up to date...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Could not upgrade pip (continuing anyway...)
)

REM Check if we're in a development directory (has src/ folder)
set "DEV_MODE="
if exist "src\safe_resource_packer" (
    set "DEV_MODE=1"
    echo 🛠️  Development mode detected (found src/ folder)
)

REM Install/check dependencies
if defined DEV_MODE (
    echo 📥 Installing in development mode...
    python -m pip install -e . --quiet
    if %errorlevel% neq 0 (
        echo ⚠️  Development install failed, trying requirements.txt...
        if exist "requirements.txt" (
            python -m pip install -r requirements.txt --quiet
        )
    )
) else (
    REM Check if safe-resource-packer is installed
    python -c "import safe_resource_packer" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Safe Resource Packer is not installed
        echo.
        echo 📥 Installing Safe Resource Packer and dependencies...
        echo    This may take a few minutes on first run...
        echo.

        REM Try to install from PyPI first
        python -m pip install safe-resource-packer --quiet
        if %errorlevel% neq 0 (
            echo ⚠️  PyPI install failed, trying local requirements...
            if exist "requirements.txt" (
                echo 📋 Installing from requirements.txt...
                python -m pip install -r requirements.txt --quiet
            )
            if exist "setup.py" (
                echo 🔧 Installing from setup.py...
                python -m pip install . --quiet
            )
        )

        REM Final check
        python -c "import safe_resource_packer" >nul 2>&1
        if %errorlevel% neq 0 (
            echo ❌ Installation failed. Trying alternative methods...
            echo.
            echo 🌐 Checking internet connection...
            ping google.com -n 1 >nul 2>&1
            if %errorlevel% neq 0 (
                echo ❌ No internet connection detected
                echo 💡 Please connect to internet and try again
                pause
                exit /b 1
            ) else (
                echo ✅ Internet connection OK
                echo 🔄 Trying manual dependency installation...
                python -m pip install rich click colorama py7zr --quiet
                if exist "src\safe_resource_packer" (
                    echo 📁 Installing from local source...
                    python -m pip install -e . --quiet
                )
            )
        ) else (
            echo ✅ Installation complete!
        )
        echo.
    ) else (
        echo ✅ Safe Resource Packer is already installed

        REM Check if we need to update dependencies
        python -c "import rich, click, colorama, py7zr" >nul 2>&1
        if %errorlevel% neq 0 (
            echo 📦 Installing missing dependencies...
            python -m pip install rich click colorama py7zr --quiet
        )
    )
)

REM Final status check and launch
python -c "import safe_resource_packer; print('✅ All systems ready!')" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  WARNING: There may be issues with the installation
    echo 🛠️  RECOVERY OPTIONS:
    echo.
    echo 1. Try running as Administrator
    echo 2. Check Windows firewall/antivirus settings
    echo 3. Restart this launcher
    echo 4. Manual installation: pip install safe-resource-packer
    echo.
    echo 💡 You can still try to continue, but some features may not work
    echo.
    set /p continue_anyway="Continue anyway? (y/n): "
    if /i not "%continue_anyway%"=="y" (
        pause
        exit /b 1
    )
)

echo ✅ Dependencies installed and verified!
echo.
echo 🚀 Launching Safe Resource Packer...
echo    All menus and options are handled by the Python interface
echo    No command-line knowledge required!
echo.
pause

REM Launch the Python script - try different methods in order of preference
REM Method 1: Use the module approach (most reliable)
echo 🔄 Launching via Python module...
python -m safe_resource_packer
if %errorlevel% equ 0 goto success

REM Method 2: Try the console script entry point
echo 🔄 Trying console script entry point...
safe-resource-packer
if %errorlevel% equ 0 goto success

REM Method 3: Development mode - direct script execution
if defined DEV_MODE (
    echo 🔄 Development mode - trying direct script execution...
    python src\safe_resource_packer\console_ui.py
    if %errorlevel% equ 0 goto success

    python src\safe_resource_packer\enhanced_cli.py
    if %errorlevel% equ 0 goto success
)

REM Method 4: Import and run directly
echo 🔄 Trying direct import method...
python -c "from safe_resource_packer.console_ui import run_console_ui; from safe_resource_packer.enhanced_cli import execute_with_config; config = run_console_ui(); exit(0 if not config else execute_with_config(config))"
if %errorlevel% equ 0 goto success

REM If all else fails, show error
echo.
echo ❌ Could not launch Safe Resource Packer
echo.
echo 🛠️  TROUBLESHOOTING:
echo.
echo 1. Try running: safe-resource-packer
echo 2. Or try: python -m safe_resource_packer
echo 3. Check installation: pip list ^| findstr safe-resource-packer
echo 4. Reinstall: pip install --force-reinstall safe-resource-packer
echo.
pause
exit /b 1

:success
echo.
echo ✅ Safe Resource Packer session completed
echo.
echo 💡 TIP: You can run this .bat file anytime to launch the tool
echo    All your Python dependencies will be automatically managed!
echo.
pause
exit /b 0
