@echo off
title Safe Resource Packer - Simple Launcher
color 0B
cls

echo.
echo ================================================================================
echo                        🚀 SAFE RESOURCE PACKER 🚀
echo                      Simple Auto-Installing Launcher
echo ================================================================================
echo.
echo 🔧 This launcher will:
echo    • Check and install Python dependencies automatically
echo    • Launch the interactive Python interface
echo    • Handle all setup for you - no technical knowledge needed!
echo.

REM Check if we're in development mode
set "DEV_MODE="
if exist "src\safe_resource_packer" (
    set "DEV_MODE=1"
    echo 🛠️  Development mode detected
)

REM Check Python
echo 🔍 Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Opening download page...
    start https://www.python.org/downloads/
    echo 📥 Please install Python and check "Add to PATH", then run this again
    pause
    exit /b 1
)
echo ✅ Python found

REM Upgrade pip quietly
echo 📦 Updating pip...
python -m pip install --upgrade pip --quiet >nul 2>&1

REM Install dependencies
echo 🔄 Installing/checking dependencies...
if defined DEV_MODE (
    python -m pip install -e . --quiet >nul 2>&1
    if %errorlevel% neq 0 (
        if exist "requirements.txt" python -m pip install -r requirements.txt --quiet >nul 2>&1
    )
) else (
    python -c "import safe_resource_packer" >nul 2>&1
    if %errorlevel% neq 0 (
        echo 📥 Installing Safe Resource Packer...
        python -m pip install safe-resource-packer --quiet
        if %errorlevel% neq 0 (
            echo 📋 Trying from requirements.txt...
            if exist "requirements.txt" python -m pip install -r requirements.txt --quiet
        )
    )
)

REM Quick dependency check
python -c "import rich, click, colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing UI dependencies...
    python -m pip install rich click colorama py7zr --quiet
)

echo ✅ Setup complete!
echo.
echo 🚀 Launching Safe Resource Packer...
echo.

REM Launch - prefer module method
python -m safe_resource_packer
if %errorlevel% equ 0 goto done

REM Fallback methods
safe-resource-packer 2>nul
if %errorlevel% equ 0 goto done

if defined DEV_MODE (
    python src\safe_resource_packer\console_ui.py
    if %errorlevel% equ 0 goto done
)

echo ❌ Launch failed. Try: python -m safe_resource_packer
pause
exit /b 1

:done
echo.
echo ✅ Session completed. Run this .bat anytime to launch the tool!
pause
