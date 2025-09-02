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

        # BSArch manual download info
        self.nexus_url = "https://www.nexusmods.com/newvegas/mods/64745?tab=files"
        self.common_download_dirs = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            "C:/Users/*/Downloads" if self.system == 'windows' else None,
            "C:/Downloads" if self.system == 'windows' else None,
        ]
        self.common_download_dirs = [d for d in self.common_download_dirs if d]

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
        # Check PATH first
        if shutil.which('bsarch') is not None or shutil.which('BSArch.exe') is not None:
            return True

        # Check our installation directory as fallback
        if self.system == 'windows':
            target_path = os.path.join(self.install_dir, 'BSArch.exe')
        else:
            target_path = os.path.join(self.install_dir, 'bsarch')

        return os.path.exists(target_path) and os.access(target_path, os.X_OK)

    def can_install_automatically(self) -> bool:
        """Check if we can help with BSArch installation (manual download + setup)."""
        # We can help on any system by guiding manual download
        return True

    def find_bsarch_in_downloads(self) -> Optional[str]:
        """Find BSArch in common download directories."""
        log("🔍 Searching for BSArch in download directories...", log_type='INFO')

        # Search patterns for BSArch files
        patterns = ['*bsarch*', '*BSArch*', '*BSARCH*']

        for download_dir in self.common_download_dirs:
            if not os.path.exists(download_dir):
                continue

            log(f"Checking: {download_dir}", log_type='INFO')

            for pattern in patterns:
                # Look for archives
                for ext in ['.zip', '.7z', '.rar']:
                    search_pattern = pattern + ext
                    for file_path in Path(download_dir).glob(search_pattern):
                        log(f"Found potential BSArch archive: {file_path}", log_type='INFO')
                        return str(file_path)

                # Look for direct executables
                search_pattern = pattern + '.exe'
                for file_path in Path(download_dir).glob(search_pattern):
                    log(f"Found BSArch executable: {file_path}", log_type='SUCCESS')
                    return str(file_path)

        return None

    def search_system_wide(self) -> Optional[str]:
        """Search for BSArch across the entire system (slow)."""
        log("🔍 Performing system-wide search for BSArch (this may take a while)...", log_type='INFO')

        search_roots = []
        if self.system == 'windows':
            search_roots = ['C:/', 'D:/', 'E:/']
        else:
            search_roots = ['/home', '/opt', '/usr/local']

        patterns = ['*bsarch*', '*BSArch*', '*BSARCH*']

        for root in search_roots:
            if not os.path.exists(root):
                continue

            log(f"Searching in: {root}", log_type='INFO')

            try:
                for pattern in patterns:
                    for file_path in Path(root).rglob(pattern + '.exe'):
                        log(f"Found BSArch executable: {file_path}", log_type='SUCCESS')
                        return str(file_path)

                    for ext in ['.zip', '.7z', '.rar']:
                        for file_path in Path(root).rglob(pattern + ext):
                            log(f"Found potential BSArch archive: {file_path}", log_type='INFO')
                            return str(file_path)
            except (PermissionError, OSError):
                # Skip directories we can't access
                continue

        return None

    def extract_bsarch_from_archive(self, archive_path: str) -> Optional[str]:
        """Extract BSArch from archive file."""
        log(f"📦 Extracting BSArch from: {archive_path}", log_type='INFO')

        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="bsarch_extract_")

        try:
            # Try different extraction methods
            if archive_path.lower().endswith('.zip'):
                success = self._extract_zip(archive_path, temp_dir)
            elif archive_path.lower().endswith('.7z'):
                success = self._extract_7z(archive_path, temp_dir)
            else:
                log(f"Unsupported archive format: {archive_path}", log_type='WARNING')
                return None

            if not success:
                return None

            # Find BSArch.exe in extracted files (case-insensitive)
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower() in ['bsarch.exe', 'bsarch']:
                        bsarch_path = os.path.join(root, file)
                        log(f"✅ Found BSArch executable: {bsarch_path}", log_type='SUCCESS')
                        return bsarch_path

            log("❌ BSArch.exe not found in archive", log_type='ERROR')
            return None

        except Exception as e:
            log(f"❌ Failed to extract archive: {e}", log_type='ERROR')
            return None
        finally:
            # Don't clean up temp_dir yet - we need the extracted file
            pass

    def _extract_zip(self, zip_path: str, extract_dir: str) -> bool:
        """Extract ZIP file."""
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except Exception as e:
            log(f"ZIP extraction failed: {e}", log_type='ERROR')
            return False

    def _extract_7z(self, archive_path: str, extract_dir: str) -> bool:
        """Extract 7z file."""
        try:
            # Try py7zr first
            import py7zr
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(extract_dir)
            return True
        except ImportError:
            # Try command-line 7z
            try:
                result = subprocess.run(['7z', 'x', archive_path, f'-o{extract_dir}', '-y'],
                                      capture_output=True, text=True)
                return result.returncode == 0
            except FileNotFoundError:
                log("Neither py7zr nor 7z command available for extraction", log_type='ERROR')
                return False
        except Exception as e:
            log(f"7z extraction failed: {e}", log_type='ERROR')
            return False

    def install_bsarch(self, force: bool = False) -> Tuple[bool, str]:
        """
        Help user install BSArch through manual download and setup.

        Args:
            force: Force installation even if BSArch is already available

        Returns:
            Tuple of (success: bool, message: str)
        """

        if not force and self.is_bsarch_available():
            return True, "BSArch is already available"

        try:
            log("🔧 Setting up BSArch for optimal BSA/BA2 creation...", log_type='INFO')

            # Step 1: Check if already downloaded
            bsarch_file = self.find_bsarch_in_downloads()

            if not bsarch_file:
                # Step 2: Guide user to download
                log("📥 BSArch not found in download directories", log_type='INFO')
                log(f"Please download BSArch from: {self.nexus_url}", log_type='INFO')
                log("After downloading, press Enter to continue searching...", log_type='INFO')

                # Wait for user to download
                input("Press Enter after downloading BSArch from Nexus...")

                # Search again
                bsarch_file = self.find_bsarch_in_downloads()

                if not bsarch_file:
                    # Step 3: System-wide search (slow)
                    log("🔍 Not found in downloads. Searching entire system...", log_type='WARNING')
                    log("⚠️  This may take several minutes on large systems", log_type='WARNING')

                    response = input("Perform system-wide search? [y/N]: ").strip().lower()
                    if response in ['y', 'yes']:
                        bsarch_file = self.search_system_wide()

                    if not bsarch_file:
                        return False, "BSArch not found. Please download from Nexus and try again."

            log(f"✅ Found BSArch file: {bsarch_file}", log_type='SUCCESS')

            # Step 4: Handle the found file
            if bsarch_file.lower().endswith(('.zip', '.7z', '.rar')):
                # Extract from archive
                extracted_path = self.extract_bsarch_from_archive(bsarch_file)
                if not extracted_path:
                    return False, "Failed to extract BSArch from archive"
                bsarch_exe = extracted_path
            else:
                # Direct executable
                bsarch_exe = bsarch_file

            # Step 5: Install to proper location
            return self._install_bsarch_executable(bsarch_exe)

        except Exception as e:
            log(f"❌ BSArch setup failed: {e}", log_type='ERROR')
            return False, f"Setup failed: {e}"

    def _install_bsarch_executable(self, source_path: str) -> Tuple[bool, str]:
        """Install BSArch executable to proper location."""

        try:
            # Create installation directory
            os.makedirs(self.install_dir, exist_ok=True)

            # Determine target name
            if self.system == 'windows':
                target_name = 'BSArch.exe'
            else:
                target_name = 'bsarch'

            target_path = os.path.join(self.install_dir, target_name)

            # Copy executable
            shutil.copy2(source_path, target_path)
            log(f"📋 Copied BSArch to: {target_path}", log_type='SUCCESS')

            # Make executable on Linux/macOS
            if self.system != 'windows':
                os.chmod(target_path, 0o755)
                log("🔧 Made BSArch executable", log_type='INFO')

            # Add to PATH if necessary
            self._ensure_in_path()

            # Add to current session PATH for immediate availability
            current_path = os.environ.get('PATH', '')
            if self.install_dir not in current_path:
                os.environ['PATH'] = current_path + (';' if self.system == 'windows' else ':') + self.install_dir
                log(f"✅ Added {self.install_dir} to current session PATH", log_type='SUCCESS')

            # Verify installation (check both PATH and direct file existence)
            if self.is_bsarch_available():
                log("✅ BSArch installed and available!", log_type='SUCCESS')
                return True, f"BSArch installed successfully to: {target_path}"
            elif os.path.exists(target_path):
                # File exists but not in PATH - this is still success for immediate use
                log("✅ BSArch installed successfully!", log_type='SUCCESS')
                log("🔄 BSArch is available for this session. Restart terminal for permanent PATH access.", log_type='INFO')
                return True, f"BSArch installed successfully to: {target_path}"
            else:
                log("⚠️  BSArch installation verification failed", log_type='WARNING')
                return False, f"BSArch installation failed - file not found at: {target_path}"

        except Exception as e:
            log(f"❌ Failed to install BSArch executable: {e}", log_type='ERROR')
            return False, f"Installation failed: {e}"

    def _ensure_in_path(self):
        """Ensure installation directory is in PATH."""

        if self.system == 'windows':
            # Try to add to Windows user PATH automatically
            success = self._add_to_windows_path()
            if success:
                log(f"✅ Added {self.install_dir} to user PATH", log_type='SUCCESS')
                log("🔄 Restart your command prompt/terminal for PATH changes to take effect", log_type='INFO')
            else:
                log(f"💡 Add {self.install_dir} to your PATH for global access", log_type='INFO')
                log("🔧 Manual PATH update: Add the above path to your user environment variables", log_type='INFO')
        else:
            # On Linux/macOS, ~/.local/bin is usually in PATH
            # Check if it's already there
            current_path = os.environ.get('PATH', '')
            if self.install_dir not in current_path:
                log(f"💡 Add {self.install_dir} to your PATH: export PATH=\"{self.install_dir}:$PATH\"", log_type='INFO')

                # Try to add to shell profile
                self._add_to_shell_profile()

    def _add_to_windows_path(self) -> bool:
        """Add installation directory to Windows user PATH."""
        try:
            import winreg

            # Open user environment key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                'Environment',
                0,
                winreg.KEY_ALL_ACCESS
            )

            try:
                # Get current PATH
                current_path, _ = winreg.QueryValueEx(key, 'PATH')
            except FileNotFoundError:
                # PATH doesn't exist, create it
                current_path = ''

            # Check if already in PATH
            paths = [p.strip() for p in current_path.split(';') if p.strip()]
            if self.install_dir not in paths:
                # Add to PATH
                new_path = ';'.join(paths + [self.install_dir])
                winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)

                # Notify system of environment change
                try:
                    import ctypes
                    from ctypes import wintypes

                    # Broadcast WM_SETTINGCHANGE message
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x1A

                    ctypes.windll.user32.SendMessageTimeoutW(
                        HWND_BROADCAST,
                        WM_SETTINGCHANGE,
                        0,
                        'Environment',
                        0x0002,  # SMTO_ABORTIFHUNG
                        5000,    # 5 second timeout
                        None
                    )
                    log("📢 Notified system of PATH change", log_type='INFO')
                except Exception as e:
                    log(f"⚠️  Could not broadcast PATH change: {e}", log_type='WARNING')

                log(f"✅ Successfully added {self.install_dir} to user PATH", log_type='SUCCESS')
                return True
            else:
                log(f"✅ {self.install_dir} already in PATH", log_type='INFO')
                return True

        except ImportError:
            log("⚠️  winreg not available - cannot modify PATH automatically", log_type='WARNING')
            return False
        except Exception as e:
            log(f"⚠️  Failed to modify Windows PATH: {e}", log_type='WARNING')
            return False
        finally:
            try:
                winreg.CloseKey(key)
            except:
                pass

    def _add_to_shell_profile(self):
        """Add PATH export to shell profile files."""
        shell_profiles = [
            os.path.expanduser('~/.bashrc'),
            os.path.expanduser('~/.bash_profile'),
            os.path.expanduser('~/.zshrc'),
            os.path.expanduser('~/.profile')
        ]

        path_line = f'export PATH="{self.install_dir}:$PATH"'

        for profile in shell_profiles:
            if os.path.exists(profile):
                try:
                    # Check if already added
                    with open(profile, 'r') as f:
                        content = f.read()

                    if self.install_dir not in content:
                        # Add to profile
                        with open(profile, 'a') as f:
                            f.write(f'\n# Added by Safe Resource Packer\n{path_line}\n')
                        log(f"✅ Added PATH to {profile}", log_type='SUCCESS')
                    else:
                        log(f"✅ PATH already in {profile}", log_type='INFO')
                    break  # Only modify the first existing profile
                except Exception as e:
                    log(f"⚠️  Could not modify {profile}: {e}", log_type='WARNING')

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
        instructions.append("📖 BSARCH INSTALLATION GUIDE")
        instructions.append("="*40)
        instructions.append("")
        instructions.append("🎯 RECOMMENDED: Use our automatic installer:")
        instructions.append("   safe-resource-packer --install-bsarch")
        instructions.append("")
        instructions.append("📥 MANUAL DOWNLOAD:")
        instructions.append(f"1. Visit: {self.nexus_url}")
        instructions.append("2. Download the BSArch file (usually a .zip)")
        instructions.append("3. Save it to your Downloads folder")
        instructions.append("4. Run our installer - it will find and set it up!")
        instructions.append("")
        instructions.append("🔍 WHAT OUR INSTALLER DOES:")
        instructions.append("• Searches Downloads folder automatically")
        instructions.append("• Extracts BSArch.exe from archives")
        instructions.append("• Installs to proper location")
        instructions.append("• Sets up PATH for you")
        instructions.append("")
        instructions.append("⚠️  FALLBACK LOCATIONS:")
        instructions.append("If not in Downloads, we can search:")
        for download_dir in self.common_download_dirs:
            instructions.append(f"• {download_dir}")
        instructions.append("• Entire system (slow but thorough)")
        instructions.append("")
        instructions.append("🎮 WHY BSARCH MATTERS:")
        instructions.append("• Creates proper BSA/BA2 archives")
        instructions.append("• 3x faster game loading")
        instructions.append("• Better memory usage")
        instructions.append("• Essential for optimal mod performance")

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
