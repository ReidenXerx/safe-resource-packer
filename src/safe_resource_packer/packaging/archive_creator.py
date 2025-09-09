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

            # Build BSArch command with proper escaping
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

            # Log the command being executed (for debugging)
            log(f"Executing BSArch: {' '.join(cmd)}", debug_only=True, log_type='INFO')

            # Execute BSArch with extended timeout for large archives
            timeout = 300 + (len(files) // 100) * 60  # Base 5min + 1min per 100 files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

            # Clean up temp directory regardless of success
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as cleanup_error:
                log(f"Warning: Failed to cleanup temp directory: {cleanup_error}", log_type='WARNING')

            if result.returncode == 0:
                # Verify the archive was actually created
                if os.path.exists(archive_path):
                    archive_size = os.path.getsize(archive_path)
                    log(f"Archive created: {archive_path} ({format_bytes(archive_size)})", log_type='SUCCESS')
                    return True, f"Archive created successfully with BSArch ({format_bytes(archive_size)})"
                else:
                    return False, "BSArch completed but archive file not found"
            else:
                error_msg = result.stderr or "Unknown BSArch error"
                log(f"BSArch stderr: {error_msg}", debug_only=True, log_type='ERROR')
                return False, f"BSArch failed: {error_msg}"

        except subprocess.TimeoutExpired:
            # Clean up temp directory on timeout
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            return False, f"BSArch timed out after {timeout // 60} minutes"
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
                files_added = 0
                total_size = 0
                
                # Log what we're trying to archive
                log(f"Creating ZIP with {len(files)} files:", log_type='INFO')
                for i, file_path in enumerate(files[:5]):  # Show first 5 files
                    if os.path.exists(file_path):
                        size_kb = os.path.getsize(file_path) / 1024
                        log(f"  • {os.path.basename(file_path)}: {size_kb:.1f} KB", log_type='INFO')
                    else:
                        log(f"  • {os.path.basename(file_path)}: NOT FOUND", log_type='ERROR')
                if len(files) > 5:
                    log(f"  • ... and {len(files) - 5} more files", log_type='INFO')
                
                for file_path in files:
                    if os.path.exists(file_path):
                        try:
                            # Use a safer approach for archive names
                            if len(files) == 1:
                                # Single file - use just the filename
                                arcname = os.path.basename(file_path)
                            else:
                                # Multiple files - try to maintain structure
                                try:
                                    common_path = os.path.commonpath(files)
                                    arcname = os.path.relpath(file_path, common_path)
                                except ValueError:
                                    # Files are on different drives or no common path
                                    arcname = os.path.basename(file_path)
                            
                            zipf.write(file_path, arcname)
                            files_added += 1
                            total_size += os.path.getsize(file_path)
                        except Exception as e:
                            log(f"Failed to add {file_path} to archive: {e}", log_type='ERROR')
                    else:
                        log(f"File not found for archiving: {file_path}", log_type='ERROR')
                
                log(f"ZIP archive created: {files_added} files, {total_size / 1024:.1f} KB total", log_type='INFO')

            # Verify the ZIP file was created and has the expected size
            if os.path.exists(zip_path):
                actual_size = os.path.getsize(zip_path)
                log(f"ZIP file verification: {actual_size} bytes on disk", log_type='INFO')
                if actual_size < 100:  # Less than 100 bytes is suspicious
                    log(f"WARNING: ZIP file is suspiciously small ({actual_size} bytes)", log_type='WARNING')
            else:
                log(f"ERROR: ZIP file not found after creation: {zip_path}", log_type='ERROR')
                return False, f"ZIP file not found after creation: {zip_path}"

            # Log the warning but return just the path
            log(f"⚠️  ZIP archive created (install BSArch for proper {archive_type})", log_type='WARNING')
            return True, zip_path

        except Exception as e:
            return False, f"Fallback archive creation failed: {e}"

    def _find_bsarch(self) -> Optional[str]:
        """Find BSArch executable in PATH or common locations."""

        # Check PATH first
        if shutil.which("bsarch"):
            return "bsarch"
        if shutil.which("BSArch.exe"):
            return "BSArch.exe"

        # Check Safe Resource Packer installation directory
        import platform
        system = platform.system().lower()
        if system == 'windows':
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            srp_path = os.path.join(appdata, 'SafeResourcePacker', 'tools', 'BSArch.exe')
            if os.path.exists(srp_path):
                return srp_path
        else:
            local_path = os.path.expanduser('~/.local/bin/bsarch')
            if os.path.exists(local_path):
                return local_path

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

