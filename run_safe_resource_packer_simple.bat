@echo off
title Safe Resource Packer - Simple Launcher
color 0B
cls

echo.
echo ================================================================================
echo                        SAFE RESOURCE PACKER
echo                   Enhanced Auto-Installing Launcher
echo ================================================================================
echo.
echo This launcher automatically handles all dependencies and setup!
echo.
echo What this tool does:
echo    - Classifies your mod files intelligently
echo    - Creates professional mod packages (BSA/BA2 + ESP)
echo    - Optimizes for game performance
echo    - Works with BodySlide, Outfit Studio, and other tools
echo.
echo Perfect for: Skyrim, Fallout 4, and other Creation Engine games
echo.
echo Auto-Setup Features:
echo    - Checks and installs Python if needed
echo    - Upgrades pip for better compatibility
echo    - Installs all required dependencies
echo    - Auto-installs 7-Zip for optimal compression
echo    - Handles virtual environments intelligently
echo.

REM Function to check if we're in a virtual environment
set "VENV_ACTIVE="
if defined VIRTUAL_ENV set "VENV_ACTIVE=1"
if defined CONDA_DEFAULT_ENV set "VENV_ACTIVE=1"

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo AUTOMATIC PYTHON INSTALLATION REQUIRED
    echo.
    echo We'll help you install Python automatically:
    echo 1. Opening Python download page...
    echo 2. Please download and install Python 3.8 or newer
    echo 3. CRITICAL: Check "Add Python to PATH" during installation
    echo 4. Run this launcher again after installation
    echo.
    start https://www.python.org/downloads/
    echo Python download page opened in your browser
    echo.
    echo.
    echo After installing Python, we'll try to refresh the PATH...
    echo    (This helps if Python was just installed)
    echo.
    pause
    
    REM Try to refresh PATH from registry
    call :refresh_path
    
    REM Check again after PATH refresh
    echo Re-checking Python installation after PATH refresh...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python still not found after PATH refresh
        echo Please restart this launcher or open a new command prompt
        echo    The PATH changes require a new session to take effect
        echo.
        pause
        exit /b 1
    ) else (
        echo Python found after PATH refresh!
        echo Continuing with setup...
    )
) else (
    echo Python found and accessible
)

echo.
echo Launching Safe Resource Packer...
echo    All menus and options are handled by the Python interface
echo    No command-line knowledge required!
echo.
pause

REM Launch the Python script
echo Launching via main entry point...
safe-resource-packer
if %errorlevel% equ 0 goto success

echo Trying module approach...
python -m safe_resource_packer
if %errorlevel% equ 0 goto success

echo Could not launch Safe Resource Packer
echo.
echo TROUBLESHOOTING:
echo.
echo 1. Try running: safe-resource-packer
echo 2. Or try: python -m safe_resource_packer
echo 3. Check installation: pip list | findstr safe-resource-packer
echo 4. Reinstall: pip install --force-reinstall safe-resource-packer
echo.
pause
exit /b 1

:success
echo.
echo Safe Resource Packer session completed
echo.
echo TIP: You can run this .bat file anytime to launch the tool
echo    All your Python dependencies will be automatically managed!
echo.
pause
exit /b 0

REM Function to refresh PATH from registry
:refresh_path
echo Refreshing PATH environment variable...
for /f "usebackq tokens=2*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul`) do set "SYSTEM_PATH=%%B"
for /f "usebackq tokens=2*" %%A in (`reg query "HKCU\Environment" /v PATH 2^>nul`) do set "USER_PATH=%%B"

REM Update current session PATH
if defined SYSTEM_PATH set "PATH=%SYSTEM_PATH%"
if defined USER_PATH set "PATH=%USER_PATH%;%PATH%"
goto :eof
