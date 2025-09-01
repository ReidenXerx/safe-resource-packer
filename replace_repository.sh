#!/bin/bash

# Safe Resource Packer - Repository Replacement Script
# This script will completely replace an existing GitHub repository with the new implementation

echo "🚀 Safe Resource Packer - Repository Replacement Script"
echo "======================================================"
echo ""
echo "This script will COMPLETELY REPLACE an existing repository with this new implementation."
echo "⚠️  WARNING: This will permanently delete all existing commits, branches, and history in the remote repository!"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "src/safe_resource_packer" ]; then
    echo "❌ Error: This script must be run from the safe-resource-packer project directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository"
    exit 1
fi

echo "📋 Current repository status:"
echo "Branch: $(git branch --show-current)"
echo "Commits: $(git rev-list --count HEAD)"
echo ""

# Prompt for repository URL
read -p "🔗 Enter your GitHub repository URL (e.g., https://github.com/username/safe-resource-packer.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL cannot be empty"
    exit 1
fi

echo ""
echo "📊 Repository Summary:"
echo "  - Complete Python package with modular structure"
echo "  - CLI interface: safe-resource-packer command"
echo "  - Comprehensive documentation and examples"
echo "  - Unit tests for all core functionality"
echo "  - Ready for PyPI distribution"
echo ""

# Final confirmation
read -p "⚠️  Are you ABSOLUTELY SURE you want to completely replace the remote repository? (type 'YES' to confirm): " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "❌ Operation cancelled"
    exit 1
fi

echo ""
echo "🔄 Starting repository replacement..."

# Remove any existing remote
git remote remove origin 2>/dev/null || true

# Add the new remote
echo "📡 Adding remote repository..."
git remote add origin "$REPO_URL"

# Verify remote was added
if ! git remote -v | grep -q origin; then
    echo "❌ Error: Failed to add remote repository"
    exit 1
fi

echo "✅ Remote added successfully"

# Force push to completely replace the remote repository
echo "🚀 Force pushing to replace remote repository..."
echo "   This will completely replace all content in the remote repository..."

if git push -f origin main; then
    echo ""
    echo "🎉 SUCCESS! Repository has been completely replaced!"
    echo ""
    echo "📊 What was replaced:"
    echo "  ✅ Complete Safe Resource Packer Python package"
    echo "  ✅ Modular code structure (core, classifier, utils, CLI)"
    echo "  ✅ Comprehensive documentation (README, API, Usage, Contributing)"
    echo "  ✅ Example scripts for Skyrim/Fallout modding"
    echo "  ✅ Unit test suite"
    echo "  ✅ Proper Python packaging (setup.py, pyproject.toml)"
    echo "  ✅ MIT License"
    echo ""
    echo "🔗 Repository URL: $REPO_URL"
    echo "🌿 Branch: main"
    echo ""
    echo "📥 Next steps:"
    echo "  1. Visit your repository on GitHub to verify the replacement"
    echo "  2. Update any documentation links if needed"
    echo "  3. Consider creating a release tag: git tag v1.0.0 && git push origin v1.0.0"
    echo "  4. Test installation: pip install git+$REPO_URL"
else
    echo ""
    echo "❌ Error: Failed to push to remote repository"
    echo "   This could be due to:"
    echo "   - Incorrect repository URL"
    echo "   - Authentication issues"
    echo "   - Network connectivity problems"
    echo "   - Repository permissions"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Verify the repository URL is correct"
    echo "   - Ensure you have push access to the repository"
    echo "   - Check your Git credentials (git config --list)"
    echo "   - Try: git push -f origin main --verbose"
    exit 1
fi
