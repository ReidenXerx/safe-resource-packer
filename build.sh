#!/bin/bash

# Safe Resource Packer - Build Release Script
# npm run build equivalent for Unix/Linux/macOS

echo "================================================================================"
echo "                     SAFE RESOURCE PACKER - BUILD RELEASE"
echo "                         npm run build equivalent"
echo "================================================================================"
echo ""
echo "This script creates a complete release package with:"
echo "  - Python wheel and source distributions"
echo "  - Portable ZIP with batch launcher"
echo "  - Source code ZIP"
echo "  - Release information"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python and try again."
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python: $PYTHON_CMD"
echo "Starting build process..."
echo ""

# Run the build script
$PYTHON_CMD build_release.py

echo ""
echo "Build script completed!"
echo "Check the 'dist/' and 'release/' directories for output files."
