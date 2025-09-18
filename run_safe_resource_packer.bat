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
echo    • Auto-installs 7-Zip for optimal compression
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
    echo.
    echo 🔄 After installing Python, we'll try to refresh the PATH...
    echo    (This helps if Python was just installed)
    echo.
    pause
    
    REM Try to refresh PATH from registry
    call :refresh_path
    
    REM Check again after PATH refresh
    echo 🔍 Re-checking Python installation after PATH refresh...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python still not found after PATH refresh
        echo 💡 Please restart this launcher or open a new command prompt
        echo    The PATH changes require a new session to take effect
        echo.
        pause
        exit /b 1
    ) else (
        echo ✅ Python found after PATH refresh!
        echo 🎉 Continuing with setup...
    )
) else (
    echo ✅ Python found and accessible
)

REM Check and upgrade pip
echo 🔄 Checking pip version...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  pip not found, trying to install...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Failed to install pip
        echo 🔄 Trying PATH refresh and retry...
        call :refresh_path
        python -m pip --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo ❌ pip still not found after PATH refresh
            echo 💡 Please restart this launcher or check Python installation
            pause
            exit /b 1
        ) else (
            echo ✅ pip found after PATH refresh!
        )
    )
)

echo 📦 Ensuring pip is up to date...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Could not upgrade pip (continuing anyway...)
)

REM Check and install 7-Zip for optimal compression performance
echo 🗜️  Checking 7-Zip installation...
set "SEVENZ_FOUND="

REM Check for high-quality 7-Zip installations
if exist "C:\Program Files\7-Zip\7z.exe" (
    set "SEVENZ_FOUND=1"
    echo ✅ 7-Zip found: C:\Program Files\7-Zip\7z.exe
    goto sevenz_check_done
)

if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
    set "SEVENZ_FOUND=1"
    echo ✅ 7-Zip found: C:\Program Files (x86)\7-Zip\7z.exe
    goto sevenz_check_done
)

REM Check PATH for 7z commands (but be careful of Windows built-in)
7z >nul 2>&1
if %errorlevel% equ 0 (
    set "SEVENZ_FOUND=1"
    echo ✅ 7-Zip found in PATH
    goto sevenz_check_done
)

7za >nul 2>&1
if %errorlevel% equ 0 (
    set "SEVENZ_FOUND=1"
    echo ✅ 7-Zip standalone found in PATH
    goto sevenz_check_done
)

:sevenz_check_done

if not defined SEVENZ_FOUND (
    echo ❌ 7-Zip not found - installing for optimal compression performance...
    echo.
    echo 🚀 AUTOMATIC 7-ZIP INSTALLATION
    echo.
    echo 7-Zip provides much faster multithreaded compression than built-in tools.
    echo This significantly improves mod packaging speed!
    echo.
    
    REM Check if Chocolatey is available
    echo 🔍 Checking for Chocolatey...
    choco --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo 🍫 Using Chocolatey to install 7-Zip...
        choco install 7zip -y --no-progress --limit-output
        if %errorlevel% equ 0 (
            echo ✅ 7-Zip installed successfully via Chocolatey!
            set "SEVENZ_FOUND=1"
        ) else (
            echo ⚠️  Chocolatey install failed, trying alternative method...
        )
    ) else (
        echo 💡 Chocolatey not found, trying direct download...
    )
    
    if not defined SEVENZ_FOUND (
        echo 📥 Downloading and installing 7-Zip directly...
        echo    This may take a moment...
        
        REM Try to download and install 7-Zip silently
        echo 🌐 Attempting direct download from 7-zip.org...
        powershell -ExecutionPolicy Bypass -Command "try { Write-Host '📥 Downloading 7-Zip installer...'; $url = 'https://www.7-zip.org/a/7z2301-x64.exe'; $output = \"$env:TEMP\7zip_installer.exe\"; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing; Write-Host '🔧 Installing 7-Zip silently...'; Start-Process -FilePath $output -ArgumentList '/S' -Wait; Remove-Item $output -Force -ErrorAction SilentlyContinue; Write-Host '✅ 7-Zip installation completed!'; exit 0 } catch { Write-Host '❌ Download failed:' $_.Exception.Message; exit 1 }" 2>nul
        
        if %errorlevel% equ 0 (
            echo ✅ 7-Zip installed successfully!
            set "SEVENZ_FOUND=1"
        ) else (
            echo ⚠️  Automatic installation failed
            echo 💡 Please install 7-Zip manually from: https://www.7-zip.org/
            echo    For best performance, use the full installer (not just 7za.exe)
            echo    The tool will work without it, but compression will be slower
            echo.
            echo ⏭️  Continuing with Python dependencies...
        )
    )
    echo.
) else (
    echo ✅ 7-Zip is ready for optimal compression performance!
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
REM Method 1: Use the main console script entry point (enhanced CLI)
echo 🔄 Launching via main entry point...
safe-resource-packer
if %errorlevel% equ 0 goto success

REM Method 2: Try the console UI entry point
echo 🔄 Trying console UI entry point...
safe-resource-packer-ui
if %errorlevel% equ 0 goto success

REM Method 3: Use the module approach (fallback)
echo 🔄 Trying module approach...
python -m safe_resource_packer
if %errorlevel% equ 0 goto success

REM Method 4: Development mode - direct script execution
if defined DEV_MODE (
    echo 🔄 Development mode - trying direct script execution...
    python src\safe_resource_packer\enhanced_cli.py
    if %errorlevel% equ 0 goto success

    python src\safe_resource_packer\console_ui.py
    if %errorlevel% equ 0 goto success
)

REM If all else fails, show error
echo.
echo ❌ Could not launch Safe Resource Packer
echo.
echo 🛠️  TROUBLESHOOTING:
echo.
echo 1. Try running: safe-resource-packer
echo 2. Or try: safe-resource-packer-ui
echo 3. Or try: python -m safe_resource_packer
echo 4. Check installation: pip list ^| findstr safe-resource-packer
echo 5. Reinstall: pip install --force-reinstall safe-resource-packer
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

REM Function to refresh PATH from registry
:refresh_path
echo 🔄 Refreshing PATH environment variable...
for /f "usebackq tokens=2*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul`) do set "SYSTEM_PATH=%%B"
for /f "usebackq tokens=2*" %%A in (`reg query "HKCU\Environment" /v PATH 2^>nul`) do set "USER_PATH=%%B"

REM Update current session PATH
if defined SYSTEM_PATH set "PATH=%SYSTEM_PATH%"
if defined USER_PATH set "PATH=%USER_PATH%;%PATH%"
goto :eof
