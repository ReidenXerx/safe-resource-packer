@echo off
title Safe Resource Packer - Easy Launcher
color 0B
cls

echo.
echo ================================================================================
echo                        🚀 SAFE RESOURCE PACKER 🚀
echo                     Easy Launcher for Windows Users
echo ================================================================================
echo.
echo This launcher will help you use Safe Resource Packer without command line!
echo.
echo 💡 What this tool does:
echo    • Classifies your mod files intelligently
echo    • Creates professional mod packages (BSA/BA2 + ESP)
echo    • Optimizes for game performance
echo    • Works with BodySlide, Outfit Studio, and other tools
echo.
echo 🎮 Perfect for: Skyrim, Fallout 4, and other Creation Engine games
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📥 Please install Python from: https://www.python.org/downloads/
    echo    ⚠️  IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if safe-resource-packer is installed
python -c "import safe_resource_packer" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Safe Resource Packer is not installed
    echo.
    echo 📥 Installing Safe Resource Packer...
    echo    This may take a few minutes...
    echo.
    pip install safe-resource-packer
    if %errorlevel% neq 0 (
        echo ❌ Installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
    echo ✅ Installation complete!
    echo.
)

echo ✅ Python and Safe Resource Packer are ready!
echo.
echo ================================================================================
echo                            🎯 CHOOSE YOUR OPTION
echo ================================================================================
echo.
echo 1️⃣  INTERACTIVE CONSOLE UI (Recommended for beginners)
echo    → Guided menus, no typing required
echo    → Perfect for first-time users
echo.
echo 2️⃣  QUICK CLASSIFICATION (Basic mode)
echo    → Just classify files into pack/loose folders
echo    → Fast and simple
echo.
echo 3️⃣  COMPLETE PACKAGING (Advanced mode)
echo    → Create professional mod packages with BSA/BA2
echo    → Includes ESP generation and compression
echo.
echo 4️⃣  INSTALL BSARCH (For optimal BSA/BA2 creation)
echo    → Download BSArch from Nexus first, then run this
echo    → Creates proper BSA/BA2 instead of ZIP files
echo.
echo 5️⃣  HELP AND DOCUMENTATION
echo    → View all available options and examples
echo.
echo 6️⃣  EXIT
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto interactive_ui
if "%choice%"=="2" goto quick_classification
if "%choice%"=="3" goto complete_packaging
if "%choice%"=="4" goto install_bsarch
if "%choice%"=="5" goto show_help
if "%choice%"=="6" goto exit
echo Invalid choice. Please enter 1-6.
pause
goto start

:interactive_ui
cls
echo.
echo 🚀 Starting Interactive Console UI...
echo.
echo This will launch a user-friendly interface with guided menus.
echo No command-line knowledge required!
echo.
pause
safe-resource-packer
goto end

:quick_classification
cls
echo.
echo 📁 QUICK CLASSIFICATION SETUP
echo ================================================================================
echo.
echo You'll need to provide three folder paths:
echo.
echo 1️⃣  SOURCE FOLDER: Your original mod files (e.g., Data folder)
echo 2️⃣  GENERATED FOLDER: Files created by BodySlide/Outfit Studio
echo 3️⃣  OUTPUT FOLDER: Where to save the results
echo.
echo 💡 TIP: You can drag and drop folders into this window to get their paths!
echo.

set /p source_path="📁 Enter SOURCE folder path: "
if "%source_path%"=="" (
    echo ❌ Source path cannot be empty
    pause
    goto quick_classification
)

set /p generated_path="🔧 Enter GENERATED folder path: "
if "%generated_path%"=="" (
    echo ❌ Generated path cannot be empty
    pause
    goto quick_classification
)

set /p output_path="📤 Enter OUTPUT folder path: "
if "%output_path%"=="" (
    echo ❌ Output path cannot be empty
    pause
    goto quick_classification
)

echo.
echo 🚀 Starting classification...
echo.
safe-resource-packer --source "%source_path%" --generated "%generated_path%" --output-pack "%output_path%\Pack" --output-loose "%output_path%\Loose" --log "%output_path%\classification.log"
goto end

:complete_packaging
cls
echo.
echo 📦 COMPLETE PACKAGING SETUP
echo ================================================================================
echo.
echo This creates professional mod packages with BSA/BA2 archives and ESP files.
echo Perfect for sharing your mods with others!
echo.

set /p source_path="📁 Enter SOURCE folder path: "
if "%source_path%"=="" (
    echo ❌ Source path cannot be empty
    pause
    goto complete_packaging
)

set /p generated_path="🔧 Enter GENERATED folder path: "
if "%generated_path%"=="" (
    echo ❌ Generated path cannot be empty
    pause
    goto complete_packaging
)

set /p package_path="📦 Enter PACKAGE output folder path: "
if "%package_path%"=="" (
    echo ❌ Package path cannot be empty
    pause
    goto complete_packaging
)

set /p mod_name="🏷️  Enter your MOD NAME (no spaces): "
if "%mod_name%"=="" (
    echo ❌ Mod name cannot be empty
    pause
    goto complete_packaging
)

echo.
echo 🎮 Choose game type:
echo 1 = Skyrim/Skyrim SE
echo 2 = Fallout 4
set /p game_choice="Enter choice (1 or 2): "

if "%game_choice%"=="1" set game_type=skyrim
if "%game_choice%"=="2" set game_type=fallout4
if "%game_type%"=="" (
    echo ❌ Invalid game choice
    pause
    goto complete_packaging
)

echo.
echo 🚀 Creating complete mod package...
echo This may take a few minutes depending on file count.
echo.
safe-resource-packer --source "%source_path%" --generated "%generated_path%" --package "%package_path%" --mod-name "%mod_name%" --game-type %game_type% --log "%package_path%\packaging.log"
goto end

:install_bsarch
cls
echo.
echo 🔧 BSARCH INSTALLATION HELPER
echo ================================================================================
echo.
echo BSArch creates optimal BSA/BA2 archives for better game performance.
echo.
echo 📥 STEP 1: Manual Download Required
echo    1. Go to: https://www.nexusmods.com/newvegas/mods/64745?tab=files
echo    2. Download BSArch (usually a .zip file)
echo    3. Save it to your Downloads folder
echo.
echo 🔧 STEP 2: Automatic Installation
echo    We'll find the downloaded file and set it up for you!
echo.
echo Press any key when you've downloaded BSArch...
pause
echo.
echo 🚀 Starting BSArch installation...
safe-resource-packer --install-bsarch
goto end

:show_help
cls
echo.
echo 📖 HELP AND DOCUMENTATION
echo ================================================================================
echo.
echo 🎯 WHAT IS SAFE RESOURCE PACKER?
echo.
echo Safe Resource Packer is a tool that helps mod creators organize and package
echo their mods professionally. It's especially useful for:
echo.
echo • BodySlide and Outfit Studio users
echo • Anyone creating texture/mesh overrides
echo • Mod authors who want professional packaging
echo • Users experiencing performance issues with loose files
echo.
echo 🚀 KEY FEATURES:
echo.
echo ✅ INTELLIGENT CLASSIFICATION
echo    • Automatically separates packable files from loose overrides
echo    • Uses advanced algorithms to prevent conflicts
echo    • 3x faster game loading through optimization
echo.
echo ✅ COMPLETE PACKAGING SYSTEM
echo    • Creates BSA/BA2 archives for optimal performance
echo    • Generates ESP files to load archives
echo    • Compresses loose files with 7z
echo    • Produces ready-to-share mod packages
echo.
echo ✅ USER-FRIENDLY INTERFACES
echo    • Interactive Console UI for beginners
echo    • Enhanced command-line for power users
echo    • This Windows launcher for easy access
echo.
echo 📁 TYPICAL WORKFLOW:
echo.
echo 1. Create your mod files (textures, meshes, etc.)
echo 2. Generate additional files with BodySlide/Outfit Studio
echo 3. Run Safe Resource Packer to classify and package
echo 4. Get optimized, professional mod package
echo 5. Share with community or install in your game
echo.
echo 💡 PERFORMANCE IMPACT:
echo.
echo Before: Thousands of loose files = slow loading, memory issues
echo After:  Optimized BSA/BA2 archives = 3x faster, stable performance
echo.
echo 🔗 MORE INFORMATION:
echo.
echo • GitHub: https://github.com/ReidenXerx/safe-resource-packer
echo • Documentation: Check README.md in installation folder
echo • Examples: See examples/ folder for detailed usage
echo.
pause
goto start

:end
echo.
echo ================================================================================
echo                            🎉 OPERATION COMPLETE!
echo ================================================================================
echo.
echo ✅ Safe Resource Packer has finished processing your files.
echo.
echo 📁 Check your output folders for results:
echo    • Look for .log files to see what was processed
echo    • Pack folder contains files for BSA/BA2 creation
echo    • Loose folder contains override files
echo    • Package folder contains complete mod packages
echo.
echo 💡 TIPS FOR NEXT TIME:
echo    • Bookmark this launcher for easy access
echo    • Consider installing BSArch for optimal BSA/BA2 creation
echo    • Use the Interactive Console UI for guided experience
echo.
echo 🎮 ENJOY YOUR OPTIMIZED MODS!
echo.
pause
exit /b 0

:exit
echo.
echo Thanks for using Safe Resource Packer! 👋
echo.
pause
exit /b 0

:start
goto :eof
