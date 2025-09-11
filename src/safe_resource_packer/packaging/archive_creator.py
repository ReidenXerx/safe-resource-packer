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
from ..dynamic_progress import log
from ..utils import sanitize_filename, validate_path_length, check_disk_space, format_bytes
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

        # Try different creation methods (no ZIP fallback - ZIP is not a valid game archive format)
        methods = [
            self._create_with_bsarch,
            self._create_with_subprocess
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

        return False, "BSA/BA2 creation failed - BSArch is required for proper game archive creation. Install BSArch to continue."

    def _create_with_bsarch(self,
                           files: List[str],
                           archive_path: str,
                           mod_name: str,
                           temp_dir: Optional[str]) -> Tuple[bool, str]:
        """Create archive using universal BSArch service with chunking support."""

        try:
            # Sanitize mod name for file system compatibility
            safe_mod_name = sanitize_filename(mod_name)
            
            # Validate archive path length
            is_valid, error_msg = validate_path_length(archive_path)
            if not is_valid:
                return False, f"Archive path too long: {error_msg}"

            # Create temporary directory structure
            if not temp_dir:
                temp_dir = os.path.join(os.path.dirname(archive_path), f"temp_{safe_mod_name}")

            # Validate temp directory path length
            is_valid, error_msg = validate_path_length(temp_dir)
            if not is_valid:
                # Try shorter path
                import tempfile
                temp_dir = os.path.join(tempfile.gettempdir(), f"srp_{safe_mod_name}")
            
            # Check disk space before starting
            estimated_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            has_space, available, required = check_disk_space(os.path.dirname(archive_path), estimated_size * 2)  # 2x for temp files
            if not has_space:
                return False, f"Insufficient disk space: need {format_bytes(required)}, have {format_bytes(available)}"

            os.makedirs(temp_dir, exist_ok=True)

            # Copy files to temp directory maintaining structure
            self._stage_files(files, temp_dir)

            # Use chunked BSArch service for automatic chunking
            from ..bsarch_service import execute_bsarch_chunked_universal
            
            # Remove extension from archive_path for chunked creation
            archive_base_path = archive_path
            archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
            if archive_base_path.endswith(archive_ext):
                archive_base_path = archive_base_path[:-len(archive_ext)]
            
            success, message, created_archives = execute_bsarch_chunked_universal(
                source_dir=temp_dir,
                output_base_path=archive_base_path,
                files=files,
                game_type=self.game_type,
                max_chunk_size_gb=2.0,  # CAO-style 2GB limit
                interactive=False  # Non-interactive for ArchiveCreator
            )

            # Clean up temp directory regardless of success
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as cleanup_error:
                log(f"Warning: Failed to cleanup temp directory: {cleanup_error}", log_type='WARNING')

            if success and created_archives:
                # For single archive, return the first one (backward compatibility)
                if len(created_archives) == 1:
                    return True, f"Archive created successfully: {os.path.basename(created_archives[0])}"
                else:
                    # Multiple chunks created
                    total_size = sum(os.path.getsize(arch) for arch in created_archives)
                    return True, f"Created {len(created_archives)} chunked archives ({format_bytes(total_size)} total)"
            else:
                return False, message or "No archives were created"

        except Exception as e:
            # Clean up temp directory on exception
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
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


    def _find_bsarch(self) -> Optional[str]:
        """Find BSArch executable using global detection system."""
        try:
            from ..bsarch_detector import get_bsarch_path_global, detect_bsarch_global
            
            # First try to get cached path
            bsarch_path = get_bsarch_path_global()
            if bsarch_path:
                log(f"✅ Found BSArch (cached): {bsarch_path}", log_type='DEBUG')
                return bsarch_path
            
            # Try global detection (non-interactive for ArchiveCreator)
            success, message = detect_bsarch_global(interactive=False)
            if success:
                # Extract path from message
                if ":" in message:
                    bsarch_path = message.split(":", 1)[1].strip()
                    log(f"✅ Found BSArch (global detection): {bsarch_path}", log_type='DEBUG')
                    return bsarch_path
            
            log(f"❌ BSArch detection failed: {message}", log_type='DEBUG')
            return None
            
        except Exception as e:
            log(f"❌ Error in global BSArch detection: {e}", log_type='ERROR')
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
        """Stage files in temporary directory maintaining proper game Data structure."""

        for file_path in files:
            if not os.path.exists(file_path):
                log(f"Skipping missing file: {file_path}", log_type='WARNING')
                continue

            # Extract Data-relative path for proper game structure
            data_rel_path = self._extract_data_relative_path(file_path)
            dest_path = os.path.join(temp_dir, data_rel_path)

            # Create destination directory
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copy file
            shutil.copy2(file_path, dest_path)

    def _extract_data_relative_path(self, file_path: str) -> str:
        """
        Extract the Data folder relative path from a file path.

        This ensures files maintain proper game directory structure like:
        meshes/armor/file.nif, textures/armor/file.dds, etc.

        Args:
            file_path: Full path to the file

        Returns:
            Data-relative path (e.g., 'meshes/armor/file.nif')
        """
        # Normalize path separators
        norm_path = file_path.replace('\\', '/')

        # Common game directory names (case-insensitive)
        game_dirs = [
            'meshes', 'textures', 'sounds', 'music', 'scripts', 'interface',
            'materials', 'programs', 'shadersfx', 'vis', 'lodsettings',
            'grass', 'trees', 'terrain', 'facegen', 'facegendata',
            'actors', 'animationdata', 'animationdatasinglefile',
            'animationsetdatasinglefile', 'behaviordata', 'charactergen',
            'dialogueviews', 'effects', 'environment', 'lighting',
            'loadscreens', 'misc', 'planetdata', 'seq', 'sound',
            'strings', 'video', 'voices', 'weapons'
        ]

        # Split path into parts
        path_parts = norm_path.split('/')

        # Find the first occurrence of a game directory (case-insensitive)
        for i, part in enumerate(path_parts):
            if part.lower() in [d.lower() for d in game_dirs]:
                # Return path from this game directory onwards
                data_relative = '/'.join(path_parts[i:])
                log(f"Extracted Data path: {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # If no game directory found, look for common patterns
        for i, part in enumerate(path_parts):
            part_lower = part.lower()
            # Check for Data directory itself
            if part_lower == 'data' and i < len(path_parts) - 1:
                # Return everything after 'data' directory
                data_relative = '/'.join(path_parts[i+1:])
                log(f"Found Data folder: {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # Fallback: use the last 2-3 path components to preserve some structure
        if len(path_parts) >= 2:
            # Try to preserve at least directory/filename structure
            fallback_path = '/'.join(path_parts[-2:])
            log(f"Fallback Data path: {file_path} → {fallback_path}", debug_only=True, log_type='WARNING')
            return fallback_path
        else:
            # Last resort: just the filename
            filename = os.path.basename(file_path)
            log(f"Using filename only: {file_path} → {filename}", debug_only=True, log_type='WARNING')
            return filename

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

