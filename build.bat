@echo off
title Safe Resource Packer - Build Release
color 0A
cls

echo ================================================================================
echo                     SAFE RESOURCE PACKER - BUILD RELEASE
echo                         npm run build equivalent
echo ================================================================================
echo.
echo This script creates a complete release package with:
echo   - Python wheel and source distributions
echo   - Portable ZIP with batch launcher
echo   - Source code ZIP
echo   - Release information
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Starting build process...
echo.

REM Run the build script
python build_release.py

echo.
echo Build script completed!
echo Check the 'dist/' and 'release/' directories for output files.
echo.
pause
