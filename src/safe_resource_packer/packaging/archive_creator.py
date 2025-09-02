"""
Archive Creator - BSA/BA2 creation functionality

Handles creation of BSA (Skyrim) and BA2 (Fallout 4) archives from classified files.
Supports multiple creation methods with fallback options.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from ..utils import log
from .bsarch_installer import install_bsarch_if_needed


class ArchiveCreator:
    """Creates BSA/BA2 archives from classified pack files."""

    def __init__(self, game_type: str = "skyrim"):
        """
        Initialize archive creator.

        Args:
            game_type: Target game ("skyrim" or "fallout4")
        """
        self.game_type = game_type.lower()
        self.supported_games = {"skyrim", "fallout4"}

        if self.game_type not in self.supported_games:
            raise ValueError(f"Unsupported game type: {game_type}. Supported: {self.supported_games}")

    def create_archive(self,
                      files: List[str],
                      archive_path: str,
                      mod_name: str,
                      temp_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create BSA/BA2 archive from list of files.

        Args:
            files: List of file paths to include in archive
            archive_path: Output path for the archive
            mod_name: Name of the mod (for internal naming)
            temp_dir: Temporary directory for staging files

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not files:
            return False, "No files provided for archiving"

        # Determine archive format
        archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
        if not archive_path.endswith(archive_ext):
            # Remove existing extension and add correct one
            path_obj = Path(archive_path)
            if path_obj.suffix:
                archive_path = str(path_obj.with_suffix(archive_ext))
            else:
                archive_path = archive_path + archive_ext

        log(f"Creating {archive_ext.upper()} archive: {archive_path}", log_type='INFO')
        log(f"Including {len(files)} files in archive", log_type='INFO')

        # Try different creation methods
        methods = [
            self._create_with_bsarch,
            self._create_with_subprocess,
            self._create_fallback
        ]

        # Track if we should offer BSArch installation
        bsarch_failed = False

        for i, method in enumerate(methods):
            try:
                success, message = method(files, archive_path, mod_name, temp_dir)
                if success:
                    return True, message

                # Check if BSArch method failed
                if method == self._create_with_bsarch and "BSArch not found" in message:
                    bsarch_failed = True

                log(f"Method failed: {message}", log_type='WARNING')
            except Exception as e:
                log(f"Archive creation method failed: {e}", log_type='ERROR')
                continue

        # If BSArch failed and we're about to use fallback, offer installation
        if bsarch_failed:
            self._offer_bsarch_installation()

        return False, "All archive creation methods failed"

    def _create_with_bsarch(self,
                           files: List[str],
                           archive_path: str,
                           mod_name: str,
                           temp_dir: Optional[str]) -> Tuple[bool, str]:
        """Create archive using BSArch command line tool."""

        # Check if BSArch is available
        bsarch_cmd = self._find_bsarch()
        if not bsarch_cmd:
            return False, "BSArch not found in PATH"

        try:
            # Create temporary directory structure
            if not temp_dir:
                temp_dir = os.path.join(os.path.dirname(archive_path), f"temp_{mod_name}")

            os.makedirs(temp_dir, exist_ok=True)

            # Copy files to temp directory maintaining structure
            self._stage_files(files, temp_dir)

            # Build BSArch command
            cmd = [
                bsarch_cmd,
                "pack",
                temp_dir,
                archive_path,
                "-mt"  # Multi-threaded
            ]

            if self.game_type == "fallout4":
                cmd.extend(["-fo4", "-dds"])  # Fallout 4 format with DDS compression
            else:
                cmd.extend(["-sse"])  # Skyrim Special Edition format

            # Execute BSArch
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Clean up temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                return True, f"Archive created successfully with BSArch"
            else:
                return False, f"BSArch failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "BSArch timed out after 5 minutes"
        except Exception as e:
            return False, f"BSArch execution failed: {e}"

    def _create_with_subprocess(self,
                               files: List[str],
                               archive_path: str,
                               mod_name: str,
                               temp_dir: Optional[str]) -> Tuple[bool, str]:
        """Create archive using other command line tools."""

        # Try Archive.exe (Creation Kit tool)
        archive_exe = self._find_archive_exe()
        if archive_exe:
            try:
                return self._create_with_archive_exe(archive_exe, files, archive_path, mod_name, temp_dir)
            except Exception as e:
                log(f"Archive.exe failed: {e}", log_type='WARNING')

        return False, "No suitable command line archive tools found"

    def _create_fallback(self,
                        files: List[str],
                        archive_path: str,
                        mod_name: str,
                        temp_dir: Optional[str]) -> Tuple[bool, str]:
        """Fallback method - create a simple ZIP archive as placeholder."""

        try:
            import zipfile

            # Inform user about the limitation
            archive_type = "BSA" if archive_path.endswith('.bsa') else "BA2"
            log("⚠️  WARNING: BSA/BA2 creation tools not found!", log_type='WARNING')
            log(f"⚠️  Creating ZIP archive instead of {archive_type} (not optimal for game performance)", log_type='WARNING')
            log("💡 For optimal performance, install BSArch: https://www.nexusmods.com/newvegas/mods/64745?tab=files", log_type='INFO')
            log("💡 Or use: safe-resource-packer --install-bsarch for guided setup", log_type='INFO')

            zip_path = archive_path.replace('.bsa', '.zip').replace('.ba2', '.zip')

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        # Maintain relative path structure
                        arcname = os.path.relpath(file_path, os.path.commonpath(files))
                        zipf.write(file_path, arcname)

            return True, f"⚠️  ZIP archive created (install BSArch for proper {archive_type}): {zip_path}"

        except Exception as e:
            return False, f"Fallback archive creation failed: {e}"

    def _find_bsarch(self) -> Optional[str]:
        """Find BSArch executable in PATH or common locations."""

        # Check PATH first
        if shutil.which("bsarch"):
            return "bsarch"
        if shutil.which("BSArch.exe"):
            return "BSArch.exe"

        # Check common installation locations
        common_paths = [
            "C:/Program Files/BSArch/BSArch.exe",
            "C:/Program Files (x86)/BSArch/BSArch.exe",
            "/usr/local/bin/bsarch",
            "/opt/bsarch/bsarch"
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def _offer_bsarch_installation(self):
        """Offer to install BSArch automatically."""
        try:
            log("🔧 BSArch not found - checking if automatic installation is possible...", log_type='INFO')

            # Try automatic installation (non-interactive for now)
            if install_bsarch_if_needed(interactive=False):
                log("✅ BSArch installed successfully! Future archive creation will be optimized.", log_type='SUCCESS')
            else:
                log("💡 For optimal BSA/BA2 creation, install BSArch manually:", log_type='INFO')
                log("   https://www.nexusmods.com/skyrimspecialedition/mods/2991", log_type='INFO')
        except Exception as e:
            log(f"BSArch installation attempt failed: {e}", log_type='WARNING')

    def _find_archive_exe(self) -> Optional[str]:
        """Find Creation Kit Archive.exe."""

        common_paths = [
            "C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition/Tools/Archive/Archive.exe",
            "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4/Tools/Archive2/Archive2.exe"
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def _stage_files(self, files: List[str], temp_dir: str):
        """Stage files in temporary directory maintaining proper structure."""

        # Find common root path
        if len(files) > 1:
            common_path = os.path.commonpath(files)
        else:
            common_path = os.path.dirname(files[0])

        for file_path in files:
            if not os.path.exists(file_path):
                log(f"Skipping missing file: {file_path}", log_type='WARNING')
                continue

            # Calculate relative path from common root
            rel_path = os.path.relpath(file_path, common_path)
            dest_path = os.path.join(temp_dir, rel_path)

            # Create destination directory
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copy file
            shutil.copy2(file_path, dest_path)

    def _create_with_archive_exe(self,
                                archive_exe: str,
                                files: List[str],
                                archive_path: str,
                                mod_name: str,
                                temp_dir: Optional[str]) -> Tuple[bool, str]:
        """Create archive using Creation Kit Archive.exe."""

        # This is a placeholder - Archive.exe requires specific command formats
        # that vary between Skyrim and Fallout 4
        return False, "Archive.exe integration not yet implemented"

    def get_archive_info(self, archive_path: str) -> Dict[str, any]:
        """Get information about created archive."""

        if not os.path.exists(archive_path):
            return {"exists": False}

        stat = os.stat(archive_path)

        return {
            "exists": True,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": stat.st_ctime,
            "format": Path(archive_path).suffix.upper()
        }

