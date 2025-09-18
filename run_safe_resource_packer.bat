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
echo    - Checks Python installation
echo    - Upgrades pip for better compatibility
echo    - Installs all required dependencies
echo    - Detects 7-Zip for optimal compression
echo    - Handles virtual environments intelligently
echo.

REM Function to check if we're in a virtual environment
set "VENV_ACTIVE="
if defined VIRTUAL_ENV set "VENV_ACTIVE=1"
if defined CONDA_DEFAULT_ENV set "VENV_ACTIVE=1"

REM Check if Python is installed
echo Checking Python installation...
set "PYTHON_CMD="

REM Try different Python commands in order of preference
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    echo Python found: python
    goto python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    echo Python found: python3
    goto python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    echo Python found: py
    goto python_found
)

REM Try to find Python in common installation paths
if exist "C:\Python311\python.exe" (
    set "PYTHON_CMD=C:\Python311\python.exe"
    echo Python found: C:\Python311\python.exe
    goto python_found
)

if exist "C:\Python310\python.exe" (
    set "PYTHON_CMD=C:\Python310\python.exe"
    echo Python found: C:\Python310\python.exe
    goto python_found
)

if exist "C:\Python39\python.exe" (
    set "PYTHON_CMD=C:\Python39\python.exe"
    echo Python found: C:\Python39\python.exe
    goto python_found
)

if exist "C:\Python38\python.exe" (
    set "PYTHON_CMD=C:\Python38\python.exe"
    echo Python found: C:\Python38\python.exe
    goto python_found
)

REM Try AppData paths
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    echo Python found: %USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
    goto python_found
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe"
    echo Python found: %USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe
    goto python_found
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe"
    echo Python found: %USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe
    goto python_found
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python38\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python38\python.exe"
    echo Python found: %USERPROFILE%\AppData\Local\Programs\Python\Python38\python.exe
    goto python_found
)

REM If we get here, Python was not found
if not defined PYTHON_CMD (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo PYTHON INSTALLATION REQUIRED
    echo.
    echo Please install Python manually:
    echo.
    echo METHOD 1: Official Python Installer (Recommended)
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.8 or newer for Windows
    echo 3. Run the installer as Administrator
    echo 4. CRITICAL: Check "Add Python to PATH" checkbox
    echo 5. Click "Install Now"
    echo 6. Restart this launcher after installation
    echo.
    echo METHOD 2: Microsoft Store
    echo 1. Open Microsoft Store
    echo 2. Search for "Python 3.11" or newer
    echo 3. Install the official Python package
    echo 4. Restart this launcher after installation
    echo.
    echo METHOD 3: Command Line (Advanced)
    echo 1. Install Chocolatey: https://chocolatey.org/install
    echo 2. Run: choco install python
    echo 3. Restart this launcher after installation
    echo.
    echo TIP: After installation, open Command Prompt and type "python --version"
    echo    If it shows a version number, Python is properly installed!
    echo.
    pause
    exit /b 1
)

:python_found
echo Python found and accessible

REM Check and upgrade pip
echo Checking pip version...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found, trying to install...
    %PYTHON_CMD% -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip
        echo Trying PATH refresh and retry...
        call :refresh_path
        %PYTHON_CMD% -m pip --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo pip still not found after PATH refresh
            echo Please restart this launcher or check Python installation
            pause
            exit /b 1
        ) else (
            echo pip found after PATH refresh!
        )
    )
)

echo Ensuring pip is up to date...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo Could not upgrade pip, trying without quiet mode...
    %PYTHON_CMD% -m pip install --upgrade pip
    if %errorlevel% neq 0 (
        echo Pip upgrade failed, trying alternative method...
        %PYTHON_CMD% -m ensurepip --upgrade
        if %errorlevel% neq 0 (
            echo All pip upgrade methods failed, continuing anyway...
        ) else (
            echo Pip upgraded successfully via ensurepip
        )
    ) else (
        echo Pip upgraded successfully
    )
)

REM Check if we're in a development directory (has src/ folder)
set "DEV_MODE="
if exist "src\safe_resource_packer" (
    set "DEV_MODE=1"
    echo Development mode detected (found src/ folder)
)

REM Install/check dependencies
if defined DEV_MODE (
    echo Installing in development mode...
    echo Trying pip install -e . (editable install)...
    %PYTHON_CMD% -m pip install -e . --quiet
    if %errorlevel% neq 0 (
        echo Editable install failed, trying verbose mode...
        %PYTHON_CMD% -m pip install -e .
        if %errorlevel% neq 0 (
            echo Editable install failed, trying requirements.txt...
            if exist "requirements.txt" (
                echo Installing from requirements.txt...
                %PYTHON_CMD% -m pip install -r requirements.txt --quiet
                if %errorlevel% neq 0 (
                    echo Requirements install failed, trying verbose mode...
                    %PYTHON_CMD% -m pip install -r requirements.txt
                    if %errorlevel% neq 0 (
                        echo All development installation methods failed
                        echo Trying manual dependency installation...
                        %PYTHON_CMD% -m pip install rich click colorama py7zr
                    )
                )
            ) else (
                echo No requirements.txt found, trying manual dependencies...
                %PYTHON_CMD% -m pip install rich click colorama py7zr
            )
        )
    ) else (
        echo Development installation successful!
    )
) else (
    REM Check if safe-resource-packer is installed
    %PYTHON_CMD% -c "import safe_resource_packer" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Safe Resource Packer is not installed
        echo.
        echo Installing Safe Resource Packer and dependencies...
        echo    This may take a few minutes on first run...
        echo.

        REM Try to install from PyPI first
        echo Trying PyPI installation...
        %PYTHON_CMD% -m pip install safe-resource-packer --quiet
        if %errorlevel% neq 0 (
            echo PyPI install failed, trying verbose mode...
            %PYTHON_CMD% -m pip install safe-resource-packer
            if %errorlevel% neq 0 (
                echo PyPI install failed, trying local requirements...
                if exist "requirements.txt" (
                    echo Installing from requirements.txt...
                    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
                    if %errorlevel% neq 0 (
                        echo Requirements install failed, trying verbose mode...
                        %PYTHON_CMD% -m pip install -r requirements.txt
                    )
                )
                if exist "setup.py" (
                    echo Installing from setup.py...
                    %PYTHON_CMD% -m pip install . --quiet
                    if %errorlevel% neq 0 (
                        echo Setup.py install failed, trying verbose mode...
                        %PYTHON_CMD% -m pip install .
                    )
                )
            )
        ) else (
            echo PyPI installation successful!
        )

        REM Final check
        %PYTHON_CMD% -c "import safe_resource_packer" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Installation failed. Trying alternative methods...
            echo.
            echo Checking internet connection...
            ping google.com -n 1 >nul 2>&1
            if %errorlevel% neq 0 (
                echo No internet connection detected
                echo Please connect to internet and try again
                pause
                exit /b 1
            ) else (
                echo Internet connection OK
                echo Trying manual dependency installation...
                echo Installing core dependencies: rich, click, colorama, py7zr
                %PYTHON_CMD% -m pip install rich click colorama py7zr --quiet
                if %errorlevel% neq 0 (
                    echo Quiet install failed, trying verbose mode...
                    %PYTHON_CMD% -m pip install rich click colorama py7zr
                )
                if exist "src\safe_resource_packer" (
                    echo Installing from local source...
                    %PYTHON_CMD% -m pip install -e . --quiet
                    if %errorlevel% neq 0 (
                        echo Editable install failed, trying verbose mode...
                        %PYTHON_CMD% -m pip install -e .
                    )
                )
            )
        ) else (
            echo Installation complete!
        )
        echo.
    ) else (
        echo Safe Resource Packer is already installed

        REM Check if we need to update dependencies
        echo Checking for missing dependencies...
        %PYTHON_CMD% -c "import rich, click, colorama, py7zr" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Installing missing dependencies...
            %PYTHON_CMD% -m pip install rich click colorama py7zr --quiet
            if %errorlevel% neq 0 (
                echo Quiet install failed, trying verbose mode...
                %PYTHON_CMD% -m pip install rich click colorama py7zr
                if %errorlevel% neq 0 (
                    echo Dependency installation failed
                    echo You may need to install dependencies manually
                ) else (
                    echo Dependencies installed successfully
                )
            ) else (
                echo Dependencies installed successfully
            )
        ) else (
            echo All dependencies are already installed
        )
    )
)

REM Final status check and launch
%PYTHON_CMD% -c "import safe_resource_packer; print('All systems ready!')" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: There may be issues with the installation
    echo.
    echo TROUBLESHOOTING STEPS:
    echo 1. Try running as Administrator
    echo 2. Check Windows firewall/antivirus settings
    echo 3. Restart this launcher
    echo 4. Manual installation: %PYTHON_CMD% -m pip install safe-resource-packer
    echo 5. Check Python installation: %PYTHON_CMD% --version
    echo 6. Check pip installation: %PYTHON_CMD% -m pip --version
    echo 7. Try manual dependency install: %PYTHON_CMD% -m pip install rich click colorama py7zr
    echo.
    echo COMMON ISSUES:
    echo - Antivirus blocking pip downloads
    echo - Corporate firewall blocking PyPI
    echo - Python installed without pip
    echo - PATH not properly configured
    echo.
    echo You can still try to continue, but some features may not work
    echo.
    set /p continue_anyway="Continue anyway? (y/n): "
    if /i not "%continue_anyway%"=="y" (
        pause
        exit /b 1
    )
)

echo Dependencies installed and verified!
echo.
echo Launching Safe Resource Packer...
echo    All menus and options are handled by the Python interface
echo    No command-line knowledge required!
echo.
pause

REM Launch the Python script - try different methods in order of preference
REM Method 1: Use the main console script entry point (enhanced CLI)
echo Launching via main entry point...
safe-resource-packer
if %errorlevel% equ 0 goto success

REM Method 2: Try the console UI entry point
echo Trying console UI entry point...
safe-resource-packer-ui
if %errorlevel% equ 0 goto success

REM Method 3: Use the module approach (fallback)
echo Trying module approach...
%PYTHON_CMD% -m safe_resource_packer
if %errorlevel% equ 0 goto success

REM Method 4: Development mode - direct script execution
if defined DEV_MODE (
    echo Development mode - trying direct script execution...
    %PYTHON_CMD% src\safe_resource_packer\enhanced_cli.py
    if %errorlevel% equ 0 goto success

    %PYTHON_CMD% src\safe_resource_packer\console_ui.py
    if %errorlevel% equ 0 goto success
)

REM If all else fails, show error
echo.
echo Could not launch Safe Resource Packer
echo.
echo TROUBLESHOOTING:
echo.
echo 1. Try running: safe-resource-packer
echo 2. Or try: safe-resource-packer-ui
echo 3. Or try: %PYTHON_CMD% -m safe_resource_packer
echo 4. Check installation: %PYTHON_CMD% -m pip list | findstr safe-resource-packer
echo 5. Reinstall: %PYTHON_CMD% -m pip install --force-reinstall safe-resource-packer
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
