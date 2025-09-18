# Safe Resource Packer - PowerShell Launcher
# This version handles Unicode characters better than batch files

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                        🚀 SAFE RESOURCE PACKER 🚀" -ForegroundColor Yellow
Write-Host "                   Enhanced Auto-Installing Launcher" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This launcher automatically handles all dependencies and setup!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 What this tool does:" -ForegroundColor Yellow
Write-Host "   • Classifies your mod files intelligently" -ForegroundColor White
Write-Host "   • Creates professional mod packages (BSA/BA2 + ESP)" -ForegroundColor White
Write-Host "   • Optimizes for game performance" -ForegroundColor White
Write-Host "   • Works with BodySlide, Outfit Studio, and other tools" -ForegroundColor White
Write-Host ""
Write-Host "🎮 Perfect for: Skyrim, Fallout 4, and other Creation Engine games" -ForegroundColor Magenta
Write-Host ""

# Function to refresh PATH from registry
function Refresh-Path {
    Write-Host "🔄 Refreshing PATH environment variable..." -ForegroundColor Yellow
    
    try {
        $systemPath = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey("SYSTEM\CurrentControlSet\Control\Session Manager\Environment").GetValue("PATH")
        $userPath = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey("Environment").GetValue("PATH")
        
        if ($systemPath) { $env:PATH = $systemPath }
        if ($userPath) { $env:PATH = "$userPath;$env:PATH" }
        
        Write-Host "✅ PATH refreshed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Could not refresh PATH: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Check if Python is installed
Write-Host "🔍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
}
catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 AUTOMATIC PYTHON INSTALLATION REQUIRED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "We'll help you install Python automatically:" -ForegroundColor White
    Write-Host "1. Opening Python download page..." -ForegroundColor White
    Write-Host "2. Please download and install Python 3.8 or newer" -ForegroundColor White
    Write-Host "3. ⚠️  CRITICAL: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host "4. Run this launcher again after installation" -ForegroundColor White
    Write-Host ""
    
    Start-Process "https://www.python.org/downloads/"
    Write-Host "🌐 Python download page opened in your browser" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 After installing Python, we'll try to refresh the PATH..." -ForegroundColor Yellow
    Write-Host "   (This helps if Python was just installed)" -ForegroundColor White
    Write-Host ""
    
    Read-Host "Press Enter after installing Python"
    
    # Try to refresh PATH from registry
    Refresh-Path
    
    # Check again after PATH refresh
    Write-Host "🔍 Re-checking Python installation after PATH refresh..." -ForegroundColor Cyan
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python found after PATH refresh: $pythonVersion" -ForegroundColor Green
            Write-Host "🎉 Continuing with setup..." -ForegroundColor Green
        } else {
            throw "Python still not found"
        }
    }
    catch {
        Write-Host "❌ Python still not found after PATH refresh" -ForegroundColor Red
        Write-Host "💡 Please restart this launcher or open a new PowerShell window" -ForegroundColor Yellow
        Write-Host "   The PATH changes require a new session to take effect" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check and upgrade pip
Write-Host "🔄 Checking pip version..." -ForegroundColor Cyan
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip found and working" -ForegroundColor Green
    } else {
        throw "pip not found"
    }
}
catch {
    Write-Host "⚠️ pip not found, trying to install..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install pip" -ForegroundColor Red
        Write-Host "🔄 Trying PATH refresh and retry..." -ForegroundColor Yellow
        Refresh-Path
        $pipVersion = python -m pip --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ pip still not found after PATH refresh" -ForegroundColor Red
            Write-Host "💡 Please restart this launcher or check Python installation" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        } else {
            Write-Host "✅ pip found after PATH refresh!" -ForegroundColor Green
        }
    }
}

Write-Host "📦 Ensuring pip is up to date..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Could not upgrade pip (continuing anyway...)" -ForegroundColor Yellow
}

# Check if we're in a development directory
$devMode = Test-Path "src\safe_resource_packer"
if ($devMode) {
    Write-Host "🛠️ Development mode detected (found src/ folder)" -ForegroundColor Magenta
    Write-Host "📥 Installing in development mode..." -ForegroundColor Cyan
    python -m pip install -e . --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Development install failed, trying requirements.txt..." -ForegroundColor Yellow
        if (Test-Path "requirements.txt") {
            python -m pip install -r requirements.txt --quiet
        }
    }
} else {
    # Check if safe-resource-packer is installed
    try {
        python -c "import safe_resource_packer" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Safe Resource Packer is already installed" -ForegroundColor Green
        } else {
            throw "Not installed"
        }
    }
    catch {
        Write-Host "❌ Safe Resource Packer is not installed" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Installing Safe Resource Packer and dependencies..." -ForegroundColor Yellow
        Write-Host "   This may take a few minutes on first run..." -ForegroundColor White
        Write-Host ""
        
        # Try to install from PyPI first
        python -m pip install safe-resource-packer --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ PyPI install failed, trying local requirements..." -ForegroundColor Yellow
            if (Test-Path "requirements.txt") {
                Write-Host "📋 Installing from requirements.txt..." -ForegroundColor Cyan
                python -m pip install -r requirements.txt --quiet
            }
            if (Test-Path "setup.py") {
                Write-Host "🔧 Installing from setup.py..." -ForegroundColor Cyan
                python -m pip install . --quiet
            }
        }
        
        # Final check
        try {
            python -c "import safe_resource_packer" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Installation complete!" -ForegroundColor Green
            } else {
                throw "Still not installed"
            }
        }
        catch {
            Write-Host "❌ Installation failed. Trying alternative methods..." -ForegroundColor Red
            Write-Host ""
            Write-Host "🌐 Checking internet connection..." -ForegroundColor Cyan
            $pingResult = Test-Connection -ComputerName "google.com" -Count 1 -Quiet
            if ($pingResult) {
                Write-Host "✅ Internet connection OK" -ForegroundColor Green
                Write-Host "🔄 Trying manual dependency installation..." -ForegroundColor Yellow
                python -m pip install rich click colorama py7zr --quiet
                if (Test-Path "src\safe_resource_packer") {
                    Write-Host "📁 Installing from local source..." -ForegroundColor Cyan
                    python -m pip install -e . --quiet
                }
            } else {
                Write-Host "❌ No internet connection detected" -ForegroundColor Red
                Write-Host "💡 Please connect to internet and try again" -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        Write-Host ""
    }
}

# Final status check and launch
Write-Host "🔍 Final status check..." -ForegroundColor Cyan
try {
    python -c "import safe_resource_packer; print('✅ All systems ready!')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed and verified!" -ForegroundColor Green
    } else {
        throw "Import failed"
    }
}
catch {
    Write-Host ""
    Write-Host "⚠️ WARNING: There may be issues with the installation" -ForegroundColor Yellow
    Write-Host "🛠️ RECOVERY OPTIONS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Try running as Administrator" -ForegroundColor White
    Write-Host "2. Check Windows firewall/antivirus settings" -ForegroundColor White
    Write-Host "3. Restart this launcher" -ForegroundColor White
    Write-Host "4. Manual installation: pip install safe-resource-packer" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 You can still try to continue, but some features may not work" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Launching Safe Resource Packer..." -ForegroundColor Green
Write-Host "   All menus and options are handled by the Python interface" -ForegroundColor White
Write-Host "   No command-line knowledge required!" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"

# Launch the Python script - try different methods in order of preference
Write-Host "🔄 Launching via main entry point..." -ForegroundColor Cyan
& safe-resource-packer
if ($LASTEXITCODE -eq 0) { goto success }

Write-Host "🔄 Trying module approach..." -ForegroundColor Cyan
python -m safe_resource_packer
if ($LASTEXITCODE -eq 0) { goto success }

# If all else fails, show error
Write-Host ""
Write-Host "❌ Could not launch Safe Resource Packer" -ForegroundColor Red
Write-Host ""
Write-Host "🛠️ TROUBLESHOOTING:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Try running: safe-resource-packer" -ForegroundColor White
Write-Host "2. Or try: python -m safe_resource_packer" -ForegroundColor White
Write-Host "3. Check installation: pip list | findstr safe-resource-packer" -ForegroundColor White
Write-Host "4. Reinstall: pip install --force-reinstall safe-resource-packer" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
exit 1

:success
Write-Host ""
Write-Host "✅ Safe Resource Packer session completed" -ForegroundColor Green
Write-Host ""
Write-Host "💡 TIP: You can run this .ps1 file anytime to launch the tool" -ForegroundColor Yellow
Write-Host "   All your Python dependencies will be automatically managed!" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
exit 0
