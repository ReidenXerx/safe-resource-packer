# Safe Resource Packer - PowerShell Launcher
# For Windows users who prefer PowerShell or have execution policy restrictions

param(
    [switch]$Help,
    [switch]$Interactive,
    [switch]$InstallBSArch
)

# Set console properties
$Host.UI.RawUI.WindowTitle = "Safe Resource Packer - PowerShell Launcher"

function Write-Header {
    Clear-Host
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "                        🚀 SAFE RESOURCE PACKER 🚀" -ForegroundColor Yellow
    Write-Host "                     PowerShell Launcher for Windows" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This launcher provides an easy way to use Safe Resource Packer!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 What this tool does:" -ForegroundColor Yellow
    Write-Host "   • Classifies your mod files intelligently" -ForegroundColor White
    Write-Host "   • Creates professional mod packages (BSA/BA2 + ESP)" -ForegroundColor White
    Write-Host "   • Optimizes for game performance" -ForegroundColor White
    Write-Host "   • Works with BodySlide, Outfit Studio, and other tools" -ForegroundColor White
    Write-Host ""
    Write-Host "🎮 Perfect for: Skyrim, Fallout 4, and other Creation Engine games" -ForegroundColor Magenta
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "   ⚠️  IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Check and install 7-Zip for optimal compression
    Write-Host "🗜️  Checking 7-Zip installation..." -ForegroundColor Yellow
    $SevenZipFound = $false
    
    # Check for high-quality 7-Zip installations
    $SevenZipPaths = @(
        "${env:ProgramFiles}\7-Zip\7z.exe",
        "${env:ProgramFiles(x86)}\7-Zip\7z.exe"
    )
    
    foreach ($path in $SevenZipPaths) {
        if (Test-Path $path) {
            Write-Host "✅ 7-Zip found: $path" -ForegroundColor Green
            $SevenZipFound = $true
            break
        }
    }
    
    # Check PATH for 7z commands
    if (-not $SevenZipFound) {
        try {
            $null = Get-Command "7z" -ErrorAction Stop
            Write-Host "✅ 7-Zip found in PATH" -ForegroundColor Green
            $SevenZipFound = $true
        } catch {
            try {
                $null = Get-Command "7za" -ErrorAction Stop
                Write-Host "✅ 7-Zip standalone found in PATH" -ForegroundColor Green
                $SevenZipFound = $true
            } catch {
                # 7-Zip not found
            }
        }
    }
    
    if (-not $SevenZipFound) {
        Write-Host "❌ 7-Zip not found - installing for optimal compression performance..." -ForegroundColor Red
        Write-Host ""
        Write-Host "🚀 AUTOMATIC 7-ZIP INSTALLATION" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "7-Zip provides much faster multithreaded compression than built-in tools." -ForegroundColor Yellow
        Write-Host "This significantly improves mod packaging speed!" -ForegroundColor Yellow
        Write-Host ""
        
        # Try Chocolatey first
        try {
            $null = Get-Command "choco" -ErrorAction Stop
            Write-Host "🍫 Using Chocolatey to install 7-Zip..." -ForegroundColor Magenta
            $chocoResult = Start-Process -FilePath "choco" -ArgumentList "install", "7zip", "-y", "--no-progress" -Wait -PassThru
            if ($chocoResult.ExitCode -eq 0) {
                Write-Host "✅ 7-Zip installed successfully via Chocolatey!" -ForegroundColor Green
                $SevenZipFound = $true
            } else {
                Write-Host "⚠️  Chocolatey install failed, trying alternative method..." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "💡 Chocolatey not found, trying direct download..." -ForegroundColor Yellow
        }
        
        if (-not $SevenZipFound) {
            Write-Host "📥 Downloading and installing 7-Zip directly..." -ForegroundColor Yellow
            Write-Host "   This may take a moment..." -ForegroundColor Gray
            
            try {
                $url = "https://www.7-zip.org/a/7z2301-x64.exe"
                $output = "$env:TEMP\7zip_installer.exe"
                
                Write-Host "📥 Downloading 7-Zip installer..." -ForegroundColor Yellow
                Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
                
                Write-Host "🔧 Installing 7-Zip silently..." -ForegroundColor Yellow
                $installResult = Start-Process -FilePath $output -ArgumentList "/S" -Wait -PassThru
                Remove-Item $output -Force
                
                if ($installResult.ExitCode -eq 0) {
                    Write-Host "✅ 7-Zip installed successfully!" -ForegroundColor Green
                    $SevenZipFound = $true
                } else {
                    throw "Installation failed with exit code: $($installResult.ExitCode)"
                }
            } catch {
                Write-Host "❌ Automatic installation failed: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host "💡 Please install 7-Zip manually from: https://www.7-zip.org/" -ForegroundColor Yellow
                Write-Host "   For best performance, use the full installer (not just 7za.exe)" -ForegroundColor Yellow
                Write-Host "   The tool will work without it, but compression will be slower" -ForegroundColor Yellow
            }
        }
        Write-Host ""
    } else {
        Write-Host "✅ 7-Zip is ready for optimal compression performance!" -ForegroundColor Green
    }

    # Check Safe Resource Packer
    try {
        python -c "import safe_resource_packer" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Safe Resource Packer is installed" -ForegroundColor Green
        } else {
            throw "Package not found"
        }
    } catch {
        Write-Host "❌ Safe Resource Packer is not installed" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Installing Safe Resource Packer..." -ForegroundColor Yellow
        Write-Host "   This may take a few minutes..." -ForegroundColor Yellow
        Write-Host ""

        # Try installing from PyPI first
        pip install safe-resource-packer
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  PyPI install failed, trying manual dependency installation..." -ForegroundColor Yellow
            pip install rich click colorama py7zr
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Installation failed. Please check your internet connection." -ForegroundColor Red
                Read-Host "Press Enter to exit"
                exit 1
            }
            # Try local installation if available
            if (Test-Path "requirements.txt") {
                Write-Host "📋 Installing from requirements.txt..." -ForegroundColor Yellow
                pip install -r requirements.txt
            }
            if (Test-Path "setup.py") {
                Write-Host "🔧 Installing from local setup..." -ForegroundColor Yellow
                pip install .
            }
        }
        Write-Host "✅ Installation complete!" -ForegroundColor Green
    }

    Write-Host ""
}

function Show-Menu {
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "                            🎯 CHOOSE YOUR OPTION" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣  INTERACTIVE CONSOLE UI (Recommended for beginners)" -ForegroundColor Green
    Write-Host "   → Guided menus, no typing required" -ForegroundColor White
    Write-Host "   → Perfect for first-time users" -ForegroundColor White
    Write-Host ""
    Write-Host "2️⃣  QUICK CLASSIFICATION (Basic mode)" -ForegroundColor Blue
    Write-Host "   → Just classify files into pack/loose folders" -ForegroundColor White
    Write-Host "   → Fast and simple" -ForegroundColor White
    Write-Host ""
    Write-Host "3️⃣  COMPLETE PACKAGING (Advanced mode)" -ForegroundColor Magenta
    Write-Host "   → Create professional mod packages with BSA/BA2" -ForegroundColor White
    Write-Host "   → Includes ESP generation and compression" -ForegroundColor White
    Write-Host ""
    Write-Host "4️⃣  INSTALL BSARCH (For optimal BSA/BA2 creation)" -ForegroundColor Yellow
    Write-Host "   → Download BSArch from Nexus first, then run this" -ForegroundColor White
    Write-Host "   → Creates proper BSA/BA2 instead of ZIP files" -ForegroundColor White
    Write-Host ""
    Write-Host "5️⃣  HELP AND DOCUMENTATION" -ForegroundColor Cyan
    Write-Host "   → View all available options and examples" -ForegroundColor White
    Write-Host ""
    Write-Host "6️⃣  EXIT" -ForegroundColor Red
    Write-Host ""
}

function Get-FolderPath {
    param(
        [string]$Prompt,
        [string]$Description
    )

    Write-Host $Description -ForegroundColor Yellow
    Write-Host "💡 TIP: You can paste a path or type 'browse' to open folder picker" -ForegroundColor Cyan

    do {
        $path = Read-Host $Prompt

        if ($path -eq "browse") {
            Add-Type -AssemblyName System.Windows.Forms
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            $folderBrowser.Description = $Description
            $folderBrowser.ShowNewFolderButton = $true

            if ($folderBrowser.ShowDialog() -eq "OK") {
                $path = $folderBrowser.SelectedPath
                Write-Host "Selected: $path" -ForegroundColor Green
            } else {
                Write-Host "No folder selected. Please try again." -ForegroundColor Red
                continue
            }
        }

        if ([string]::IsNullOrWhiteSpace($path)) {
            Write-Host "❌ Path cannot be empty. Please try again." -ForegroundColor Red
            continue
        }

        # Remove quotes if present
        $path = $path.Trim('"')

        if (Test-Path $path) {
            return $path
        } else {
            Write-Host "❌ Path does not exist: $path" -ForegroundColor Red
            Write-Host "Please check the path and try again." -ForegroundColor Yellow
        }
    } while ($true)
}

function Start-InteractiveUI {
    Clear-Host
    Write-Host ""
    Write-Host "🚀 Starting Interactive Console UI..." -ForegroundColor Green
    Write-Host ""
    Write-Host "This will launch a user-friendly interface with guided menus." -ForegroundColor Yellow
    Write-Host "No command-line knowledge required!" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"

    safe-resource-packer
}

function Start-QuickClassification {
    Clear-Host
    Write-Host ""
    Write-Host "📁 QUICK CLASSIFICATION SETUP" -ForegroundColor Blue
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You'll need to provide three folder paths:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1️⃣  SOURCE FOLDER: Your original mod files (e.g., Data folder)" -ForegroundColor White
    Write-Host "2️⃣  GENERATED FOLDER: Files created by BodySlide/Outfit Studio" -ForegroundColor White
    Write-Host "3️⃣  OUTPUT FOLDER: Where to save the results" -ForegroundColor White
    Write-Host ""

    $sourcePath = Get-FolderPath "📁 Enter SOURCE folder path (or 'browse'): " "Select your source mod files folder"
    $generatedPath = Get-FolderPath "🔧 Enter GENERATED folder path (or 'browse'): " "Select your generated files folder (BodySlide output)"
    $outputPath = Get-FolderPath "📤 Enter OUTPUT folder path (or 'browse'): " "Select where to save the classification results"

    Write-Host ""
    Write-Host "🚀 Starting classification..." -ForegroundColor Green
    Write-Host ""

    $packPath = Join-Path $outputPath "Pack"
    $loosePath = Join-Path $outputPath "Loose"
    $logPath = Join-Path $outputPath "classification.log"

    safe-resource-packer --source "$sourcePath" --generated "$generatedPath" --output-pack "$packPath" --output-loose "$loosePath" --log "$logPath"
}

function Start-CompletePackaging {
    Clear-Host
    Write-Host ""
    Write-Host "📦 COMPLETE PACKAGING SETUP" -ForegroundColor Magenta
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This creates professional mod packages with BSA/BA2 archives and ESP files." -ForegroundColor Yellow
    Write-Host "Perfect for sharing your mods with others!" -ForegroundColor Yellow
    Write-Host ""

    $sourcePath = Get-FolderPath "📁 Enter SOURCE folder path (or 'browse'): " "Select your source mod files folder"
    $generatedPath = Get-FolderPath "🔧 Enter GENERATED folder path (or 'browse'): " "Select your generated files folder (BodySlide output)"
    $packagePath = Get-FolderPath "📦 Enter PACKAGE output folder path (or 'browse'): " "Select where to save the complete mod package"

    do {
        $modName = Read-Host "🏷️  Enter your MOD NAME (no spaces)"
        if ([string]::IsNullOrWhiteSpace($modName)) {
            Write-Host "❌ Mod name cannot be empty. Please try again." -ForegroundColor Red
        }
    } while ([string]::IsNullOrWhiteSpace($modName))

    Write-Host ""
    Write-Host "🎮 Choose game type:" -ForegroundColor Yellow
    Write-Host "1 = Skyrim/Skyrim SE" -ForegroundColor White
    Write-Host "2 = Fallout 4" -ForegroundColor White

    do {
        $gameChoice = Read-Host "Enter choice (1 or 2)"
        switch ($gameChoice) {
            "1" { $gameType = "skyrim"; break }
            "2" { $gameType = "fallout4"; break }
            default {
                Write-Host "❌ Invalid choice. Please enter 1 or 2." -ForegroundColor Red
                $gameType = $null
            }
        }
    } while ($null -eq $gameType)

    Write-Host ""
    Write-Host "🚀 Creating complete mod package..." -ForegroundColor Green
    Write-Host "This may take a few minutes depending on file count." -ForegroundColor Yellow
    Write-Host ""

    $logPath = Join-Path $packagePath "packaging.log"
    safe-resource-packer --source "$sourcePath" --generated "$generatedPath" --package "$packagePath" --mod-name "$modName" --game-type $gameType --log "$logPath"
}

function Install-BSArch {
    Clear-Host
    Write-Host ""
    Write-Host "🔧 BSARCH INSTALLATION HELPER" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "BSArch creates optimal BSA/BA2 archives for better game performance." -ForegroundColor Green
    Write-Host ""
    Write-Host "📥 STEP 1: Manual Download Required" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://www.nexusmods.com/newvegas/mods/64745?tab=files" -ForegroundColor White
    Write-Host "   2. Download BSArch (usually a .zip file)" -ForegroundColor White
    Write-Host "   3. Save it to your Downloads folder" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 STEP 2: Automatic Installation" -ForegroundColor Yellow
    Write-Host "   We'll find the downloaded file and set it up for you!" -ForegroundColor White
    Write-Host ""

    # Open the Nexus page
    $openPage = Read-Host "Open Nexus download page in browser? (y/n)"
    if ($openPage -eq "y" -or $openPage -eq "Y") {
        Start-Process "https://www.nexusmods.com/newvegas/mods/64745?tab=files"
    }

    Read-Host "Press Enter when you've downloaded BSArch"

    Write-Host ""
    Write-Host "🚀 Starting BSArch installation..." -ForegroundColor Green
    safe-resource-packer --install-bsarch
}

function Show-Help {
    Clear-Host
    Write-Host ""
    Write-Host "📖 HELP AND DOCUMENTATION" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎯 WHAT IS SAFE RESOURCE PACKER?" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Safe Resource Packer is a tool that helps mod creators organize and package" -ForegroundColor White
    Write-Host "their mods professionally. It's especially useful for:" -ForegroundColor White
    Write-Host ""
    Write-Host "• BodySlide and Outfit Studio users" -ForegroundColor Green
    Write-Host "• Anyone creating texture/mesh overrides" -ForegroundColor Green
    Write-Host "• Mod authors who want professional packaging" -ForegroundColor Green
    Write-Host "• Users experiencing performance issues with loose files" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 KEY FEATURES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✅ INTELLIGENT CLASSIFICATION" -ForegroundColor Green
    Write-Host "   • Automatically separates packable files from loose overrides" -ForegroundColor White
    Write-Host "   • Uses advanced algorithms to prevent conflicts" -ForegroundColor White
    Write-Host "   • 3x faster game loading through optimization" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ COMPLETE PACKAGING SYSTEM" -ForegroundColor Green
    Write-Host "   • Creates BSA/BA2 archives for optimal performance" -ForegroundColor White
    Write-Host "   • Generates ESP files to load archives" -ForegroundColor White
    Write-Host "   • Compresses loose files with 7z" -ForegroundColor White
    Write-Host "   • Produces ready-to-share mod packages" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ USER-FRIENDLY INTERFACES" -ForegroundColor Green
    Write-Host "   • Interactive Console UI for beginners" -ForegroundColor White
    Write-Host "   • Enhanced command-line for power users" -ForegroundColor White
    Write-Host "   • Windows launchers for easy access" -ForegroundColor White
    Write-Host ""
    Write-Host "📁 TYPICAL WORKFLOW:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Create your mod files (textures, meshes, etc.)" -ForegroundColor White
    Write-Host "2. Generate additional files with BodySlide/Outfit Studio" -ForegroundColor White
    Write-Host "3. Run Safe Resource Packer to classify and package" -ForegroundColor White
    Write-Host "4. Get optimized, professional mod package" -ForegroundColor White
    Write-Host "5. Share with community or install in your game" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 PERFORMANCE IMPACT:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Before: Thousands of loose files = slow loading, memory issues" -ForegroundColor Red
    Write-Host "After:  Optimized BSA/BA2 archives = 3x faster, stable performance" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 MORE INFORMATION:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "• GitHub: https://github.com/ReidenXerx/safe-resource-packer" -ForegroundColor Cyan
    Write-Host "• Documentation: Check README.md in installation folder" -ForegroundColor Cyan
    Write-Host "• Examples: See examples/ folder for detailed usage" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to return to main menu"
}

function Show-Completion {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "                            🎉 OPERATION COMPLETE!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Safe Resource Packer has finished processing your files." -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Check your output folders for results:" -ForegroundColor Yellow
    Write-Host "   • Look for .log files to see what was processed" -ForegroundColor White
    Write-Host "   • Pack folder contains files for BSA/BA2 creation" -ForegroundColor White
    Write-Host "   • Loose folder contains override files" -ForegroundColor White
    Write-Host "   • Package folder contains complete mod packages" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 TIPS FOR NEXT TIME:" -ForegroundColor Yellow
    Write-Host "   • Bookmark this launcher for easy access" -ForegroundColor White
    Write-Host "   • Consider installing BSArch for optimal BSA/BA2 creation" -ForegroundColor White
    Write-Host "   • Use the Interactive Console UI for guided experience" -ForegroundColor White
    Write-Host ""
    Write-Host "🎮 ENJOY YOUR OPTIMIZED MODS!" -ForegroundColor Magenta
    Write-Host ""
}

# Handle command line parameters
if ($Help) {
    Write-Header
    Show-Help
    exit 0
}

if ($Interactive) {
    Write-Header
    Test-Prerequisites
    Start-InteractiveUI
    Show-Completion
    Read-Host "Press Enter to exit"
    exit 0
}

if ($InstallBSArch) {
    Write-Header
    Test-Prerequisites
    Install-BSArch
    Show-Completion
    Read-Host "Press Enter to exit"
    exit 0
}

# Main menu loop
Write-Header
Test-Prerequisites

do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-6)"

    switch ($choice) {
        "1" {
            Start-InteractiveUI
            Show-Completion
            break
        }
        "2" {
            Start-QuickClassification
            Show-Completion
            break
        }
        "3" {
            Start-CompletePackaging
            Show-Completion
            break
        }
        "4" {
            Install-BSArch
            Show-Completion
            break
        }
        "5" {
            Show-Help
            Write-Header
            Test-Prerequisites
            continue
        }
        "6" {
            Write-Host ""
            Write-Host "Thanks for using Safe Resource Packer! 👋" -ForegroundColor Green
            Write-Host ""
            exit 0
        }
        default {
            Write-Host "❌ Invalid choice. Please enter 1-6." -ForegroundColor Red
            Read-Host "Press Enter to continue"
            Write-Header
            Test-Prerequisites
            continue
        }
    }

    $again = Read-Host "Would you like to perform another operation? (y/n)"
    if ($again -ne "y" -and $again -ne "Y") {
        Write-Host ""
        Write-Host "Thanks for using Safe Resource Packer! 👋" -ForegroundColor Green
        Write-Host ""
        break
    }

    Write-Header
    Test-Prerequisites

} while ($true)

Read-Host "Press Enter to exit"
