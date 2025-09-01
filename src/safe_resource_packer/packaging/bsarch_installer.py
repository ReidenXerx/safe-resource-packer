"""
BSArch Installer - Automatic BSArch installation for optimal BSA/BA2 creation

This module handles automatic download and installation of BSArch command-line tool
to enable proper BSA/BA2 archive creation instead of ZIP fallback.
"""

import os
import sys
import shutil
import platform
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlretrieve
from ..utils import log


class BSArchInstaller:
    """Handles automatic BSArch installation."""

    def __init__(self):
        """Initialize BSArch installer."""
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.install_dir = self._get_install_directory()

        # BSArch download URLs (these would need to be updated with actual URLs)
        self.download_urls = {
            'windows': {
                'x64': 'https://github.com/TES5Edit/BSArch/releases/latest/download/BSArch-x64.exe',
                'x86': 'https://github.com/TES5Edit/BSArch/releases/latest/download/BSArch-x86.exe',
            },
            'linux': {
                'x86_64': 'https://github.com/TES5Edit/BSArch/releases/latest/download/BSArch-linux-x64',
            }
        }

    def _get_install_directory(self) -> str:
        """Get appropriate installation directory for BSArch."""

        if self.system == 'windows':
            # Use AppData for Windows
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            install_dir = os.path.join(appdata, 'SafeResourcePacker', 'tools')
        else:
            # Use ~/.local/bin for Linux/macOS
            install_dir = os.path.expanduser('~/.local/bin')

        return install_dir

    def is_bsarch_available(self) -> bool:
        """Check if BSArch is already available."""
        return shutil.which('bsarch') is not None or shutil.which('BSArch.exe') is not None

    def can_install_automatically(self) -> bool:
        """Check if automatic installation is possible on this system."""

        # Check if we have download URLs for this system
        if self.system not in self.download_urls:
            return False

        arch_variants = self.download_urls[self.system]

        # Check architecture compatibility
        if self.system == 'windows':
            return 'x64' in arch_variants or 'x86' in arch_variants
        elif self.system == 'linux':
            return self.architecture in ['x86_64', 'amd64']

        return False

    def get_download_url(self) -> Optional[str]:
        """Get appropriate download URL for current system."""

        if self.system not in self.download_urls:
            return None

        arch_variants = self.download_urls[self.system]

        if self.system == 'windows':
            # Prefer x64, fallback to x86
            if 'x64' in arch_variants:
                return arch_variants['x64']
            elif 'x86' in arch_variants:
                return arch_variants['x86']
        elif self.system == 'linux':
            if self.architecture in ['x86_64', 'amd64'] and 'x86_64' in arch_variants:
                return arch_variants['x86_64']

        return None

    def install_bsarch(self, force: bool = False) -> Tuple[bool, str]:
        """
        Install BSArch automatically.

        Args:
            force: Force installation even if BSArch is already available

        Returns:
            Tuple of (success: bool, message: str)
        """

        if not force and self.is_bsarch_available():
            return True, "BSArch is already available"

        if not self.can_install_automatically():
            return False, f"Automatic installation not supported on {self.system} {self.architecture}"

        download_url = self.get_download_url()
        if not download_url:
            return False, "No download URL available for this system"

        try:
            log("🔧 Installing BSArch for optimal BSA/BA2 creation...", log_type='INFO')

            # Create installation directory
            os.makedirs(self.install_dir, exist_ok=True)

            # Determine executable name
            if self.system == 'windows':
                exe_name = 'BSArch.exe'
            else:
                exe_name = 'bsarch'

            exe_path = os.path.join(self.install_dir, exe_name)

            # Download BSArch
            log(f"📥 Downloading BSArch from: {download_url}", log_type='INFO')

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                urlretrieve(download_url, temp_file.name)
                temp_path = temp_file.name

            # Move to installation directory
            shutil.move(temp_path, exe_path)

            # Make executable on Linux/macOS
            if self.system != 'windows':
                os.chmod(exe_path, 0o755)

            # Add to PATH if necessary
            self._ensure_in_path()

            # Verify installation
            if self.is_bsarch_available():
                log("✅ BSArch installed successfully!", log_type='SUCCESS')
                return True, f"BSArch installed to: {exe_path}"
            else:
                log("⚠️  BSArch installed but not found in PATH", log_type='WARNING')
                return False, f"BSArch installed to {exe_path} but not accessible. Add {self.install_dir} to PATH."

        except Exception as e:
            log(f"❌ BSArch installation failed: {e}", log_type='ERROR')
            return False, f"Installation failed: {e}"

    def _ensure_in_path(self):
        """Ensure installation directory is in PATH."""

        if self.system == 'windows':
            # On Windows, we could modify user PATH, but it's complex
            # For now, just inform user
            log(f"💡 Add {self.install_dir} to your PATH for global access", log_type='INFO')
        else:
            # On Linux/macOS, ~/.local/bin is usually in PATH
            # Check if it's already there
            current_path = os.environ.get('PATH', '')
            if self.install_dir not in current_path:
                log(f"💡 Add {self.install_dir} to your PATH: export PATH=\"{self.install_dir}:$PATH\"", log_type='INFO')

    def prompt_user_installation(self) -> bool:
        """
        Prompt user for permission to install BSArch.

        Returns:
            True if user agrees to installation
        """

        if not self.can_install_automatically():
            return False

        try:
            print("\n" + "="*60)
            print("🔧 BSA/BA2 OPTIMIZATION AVAILABLE")
            print("="*60)
            print("For optimal game performance, BSArch can create proper BSA/BA2 archives")
            print("instead of ZIP files (3x faster loading in-game).")
            print()
            print("Would you like to automatically install BSArch? (recommended)")
            print("This will download and install BSArch command-line tool.")
            print()

            while True:
                response = input("Install BSArch automatically? [Y/n]: ").strip().lower()
                if response in ['', 'y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")

        except (KeyboardInterrupt, EOFError):
            return False

    def get_installation_instructions(self) -> str:
        """Get manual installation instructions for current system."""

        instructions = []
        instructions.append("📖 MANUAL BSARCH INSTALLATION")
        instructions.append("="*40)

        if self.system == 'windows':
            instructions.extend([
                "1. Download BSArch from:",
                "   https://www.nexusmods.com/skyrimspecialedition/mods/2991",
                "   OR: https://github.com/TES5Edit/BSArch/releases",
                "",
                "2. Extract BSArch.exe to a folder (e.g., C:\\Tools\\BSArch\\)",
                "",
                "3. Add the folder to your PATH:",
                "   - Press Win+R, type 'sysdm.cpl', press Enter",
                "   - Click 'Environment Variables'",
                "   - Edit 'Path' and add your BSArch folder",
                "",
                "4. Restart command prompt and try again"
            ])
        else:
            instructions.extend([
                "1. Download BSArch from:",
                "   https://github.com/TES5Edit/BSArch/releases",
                "",
                "2. Extract and make executable:",
                "   chmod +x bsarch",
                "",
                "3. Move to PATH directory:",
                f"   mv bsarch {self.install_dir}/",
                "",
                "4. Or add to PATH:",
                "   export PATH=\"/path/to/bsarch:$PATH\""
            ])

        return "\n".join(instructions)


def install_bsarch_if_needed(interactive: bool = True) -> bool:
    """
    Install BSArch if needed and user agrees.

    Args:
        interactive: Whether to prompt user for permission

    Returns:
        True if BSArch is available after this function
    """

    installer = BSArchInstaller()

    # Check if already available
    if installer.is_bsarch_available():
        return True

    # Check if we can install automatically
    if not installer.can_install_automatically():
        if interactive:
            print("\n" + installer.get_installation_instructions())
        return False

    # Prompt user if interactive
    if interactive:
        if not installer.prompt_user_installation():
            print("\n💡 You can install BSArch later for optimal performance.")
            print("The tool will use ZIP archives as fallback (still works, just not optimal).")
            return False

    # Install BSArch
    success, message = installer.install_bsarch()

    if success:
        log("🎉 BSArch installation completed! BSA/BA2 archives will now be created optimally.", log_type='SUCCESS')
    else:
        log(f"⚠️  BSArch installation failed: {message}", log_type='WARNING')
        if interactive:
            print("\n" + installer.get_installation_instructions())

    return success
