"""
Compressor - 7z compression functionality

Handles compression of loose files and final package assembly using 7z format.
Provides multiple compression methods with fallback options.
"""

import os
import subprocess
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from ..utils import log

try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    PY7ZR_AVAILABLE = False
    log("py7zr not available, falling back to command-line 7z", log_type='WARNING')


class Compressor:
    """Handles 7z compression for loose files and final packages."""

    def __init__(self, compression_level: int = 5):
        """
        Initialize compressor.

        Args:
            compression_level: Compression level (0-9, where 9 is maximum)
        """
        self.compression_level = max(0, min(9, compression_level))
        self.methods_tried = []

    def compress_files(self,
                      files: List[str],
                      archive_path: str,
                      base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Compress list of files into 7z archive.

        Args:
            files: List of file paths to compress
            archive_path: Output path for 7z archive
            base_dir: Base directory for relative paths (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not files:
            return False, "No files provided for compression"

        # Ensure archive has .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = Path(archive_path).with_suffix('.7z')

        log(f"Compressing {len(files)} files to: {archive_path}", log_type='INFO')

        # Try different compression methods
        methods = [
            self._compress_with_py7zr,
            self._compress_with_7z_command,
            self._compress_with_zip_fallback
        ]

        for method in methods:
            try:
                success, message = method(files, str(archive_path), base_dir)
                if success:
                    return True, message
                self.methods_tried.append(method.__name__)
                log(f"Compression method failed: {message}", log_type='WARNING')
            except Exception as e:
                log(f"Compression method error: {e}", log_type='ERROR')
                continue

        return False, f"All compression methods failed. Tried: {self.methods_tried}"

    def compress_directory(self,
                          source_dir: str,
                          archive_path: str,
                          exclude_patterns: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Compress entire directory into 7z archive.

        Args:
            source_dir: Directory to compress
            archive_path: Output path for 7z archive
            exclude_patterns: Patterns to exclude from compression

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not os.path.exists(source_dir):
            return False, f"Source directory does not exist: {source_dir}"

        # Collect all files in directory
        files = []
        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)

                # Check exclude patterns
                if exclude_patterns:
                    excluded = False
                    for pattern in exclude_patterns:
                        if pattern in file_path:
                            excluded = True
                            break
                    if excluded:
                        continue

                files.append(file_path)

        return self.compress_files(files, archive_path, source_dir)

    def _compress_with_py7zr(self,
                            files: List[str],
                            archive_path: str,
                            base_dir: Optional[str]) -> Tuple[bool, str]:
        """Compress using py7zr library."""

        if not PY7ZR_AVAILABLE:
            return False, "py7zr library not available"

        try:
            # Create filters for compression
            filters = [{"id": py7zr.FILTER_LZMA2, "preset": self.compression_level}]
            with py7zr.SevenZipFile(archive_path, 'w', filters=filters) as archive:

                for file_path in files:
                    if not os.path.exists(file_path):
                        log(f"Skipping missing file: {file_path}", log_type='WARNING')
                        continue

                    # Calculate archive name (Data-relative path for game structure)
                    if base_dir:
                        arcname = os.path.relpath(file_path, base_dir)
                    else:
                        # Extract Data-relative path for proper game structure
                        arcname = self._extract_data_relative_path(file_path)

                    archive.write(file_path, arcname)

            return True, f"Archive created with py7zr: {archive_path}"

        except Exception as e:
            return False, f"py7zr compression failed: {e}"

    def _compress_with_7z_command(self,
                                 files: List[str],
                                 archive_path: str,
                                 base_dir: Optional[str]) -> Tuple[bool, str]:
        """Compress using command-line 7z tool."""

        # Find 7z executable
        sevenz_cmd = self._find_7z_command()
        if not sevenz_cmd:
            return False, "7z command not found"

        try:
            # Create temporary file list if too many files (increased limit)
            if len(files) > 1000:
                return self._compress_with_7z_listfile(sevenz_cmd, files, archive_path, base_dir)

            # Build command - use working directory to avoid path issues
            if base_dir and os.path.exists(base_dir):
                # Change to base directory and use relative paths
                cmd = [sevenz_cmd, 'a', os.path.abspath(archive_path), f'-mx{self.compression_level}']
                relative_files = []
                for file_path in files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, base_dir)
                        relative_files.append(rel_path)
                cmd.extend(relative_files)

                # Execute from base directory
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=base_dir)
            else:
                # Use absolute paths
                cmd = [sevenz_cmd, 'a', archive_path, f'-mx{self.compression_level}']
                for file_path in files:
                    if os.path.exists(file_path):
                        cmd.append(file_path)

                # Execute 7z with absolute paths
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                return True, f"Archive created with 7z command: {archive_path}"
            else:
                return False, f"7z command failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "7z command timed out after 10 minutes"
        except Exception as e:
            return False, f"7z command execution failed: {e}"

    def _compress_with_7z_listfile(self,
                                   sevenz_cmd: str,
                                   files: List[str],
                                   archive_path: str,
                                   base_dir: Optional[str]) -> Tuple[bool, str]:
        """Compress using 7z with file list (for many files)."""

        try:
            # Create temporary file list
            listfile_path = archive_path + '.filelist'

            with open(listfile_path, 'w', encoding='utf-8') as f:
                for file_path in files:
                    if os.path.exists(file_path):
                        f.write(f'"{file_path}"\n')

            # Build command with file list
            cmd = [
                sevenz_cmd, 'a', archive_path,
                f'-mx{self.compression_level}',
                f'@{listfile_path}'
            ]

            # Execute 7z
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            # Clean up file list
            try:
                os.remove(listfile_path)
            except:
                pass

            if result.returncode == 0:
                return True, f"Archive created with 7z (filelist): {archive_path}"
            else:
                return False, f"7z filelist command failed: {result.stderr}"

        except Exception as e:
            return False, f"7z filelist compression failed: {e}"

    def _compress_with_zip_fallback(self,
                                   files: List[str],
                                   archive_path: str,
                                   base_dir: Optional[str]) -> Tuple[bool, str]:
        """Fallback compression using ZIP format."""

        try:
            zip_path = archive_path.replace('.7z', '.zip')

            log("Using fallback ZIP compression (not as efficient as 7z)", log_type='WARNING')

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED,
                               compresslevel=min(self.compression_level, 9)) as zipf:

                for file_path in files:
                    if not os.path.exists(file_path):
                        continue

                    # Calculate archive name (Data-relative path for game structure)
                    if base_dir:
                        arcname = os.path.relpath(file_path, base_dir)
                    else:
                        # Extract Data-relative path for proper game structure
                        arcname = self._extract_data_relative_path(file_path)

                    zipf.write(file_path, arcname)

            return True, f"Fallback ZIP archive created: {zip_path}"

        except Exception as e:
            return False, f"ZIP fallback compression failed: {e}"

    def _find_7z_command(self) -> Optional[str]:
        """Find 7z executable in PATH or common locations."""

        # Check PATH first
        for cmd in ['7z', '7za', '7zr', '7z.exe']:
            if shutil.which(cmd):
                return cmd

        # Check common installation locations
        common_paths = [
            "C:/Program Files/7-Zip/7z.exe",
            "C:/Program Files (x86)/7-Zip/7z.exe",
            "/usr/bin/7z",
            "/usr/local/bin/7z",
            "/opt/7z/7z"
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

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

    def get_archive_info(self, archive_path: str) -> Dict[str, any]:
        """
        Get information about compressed archive.

        Args:
            archive_path: Path to archive file

        Returns:
            Dictionary with archive information
        """
        if not os.path.exists(archive_path):
            return {"exists": False}

        stat = os.stat(archive_path)

        info = {
            "exists": True,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": stat.st_ctime,
            "format": Path(archive_path).suffix.upper(),
            "filename": os.path.basename(archive_path)
        }

        # Try to get additional info if py7zr is available
        if PY7ZR_AVAILABLE and archive_path.lower().endswith('.7z'):
            try:
                with py7zr.SevenZipFile(archive_path, 'r') as archive:
                    file_list = archive.getnames()
                    info["file_count"] = len(file_list)
                    info["files"] = file_list[:10]  # First 10 files
                    if len(file_list) > 10:
                        info["files"].append(f"... and {len(file_list) - 10} more files")
            except:
                pass

        return info

    def extract_archive(self,
                       archive_path: str,
                       extract_dir: str) -> Tuple[bool, str]:
        """
        Extract 7z archive (utility method).

        Args:
            archive_path: Path to archive to extract
            extract_dir: Directory to extract to

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not os.path.exists(archive_path):
            return False, f"Archive does not exist: {archive_path}"

        os.makedirs(extract_dir, exist_ok=True)

        # Try py7zr first
        if PY7ZR_AVAILABLE and archive_path.lower().endswith('.7z'):
            try:
                with py7zr.SevenZipFile(archive_path, 'r') as archive:
                    archive.extractall(extract_dir)
                return True, f"Extracted with py7zr to: {extract_dir}"
            except Exception as e:
                log(f"py7zr extraction failed: {e}", log_type='WARNING')

        # Try command-line 7z
        sevenz_cmd = self._find_7z_command()
        if sevenz_cmd:
            try:
                cmd = [sevenz_cmd, 'x', archive_path, f'-o{extract_dir}', '-y']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    return True, f"Extracted with 7z command to: {extract_dir}"
                else:
                    return False, f"7z extraction failed: {result.stderr}"
            except Exception as e:
                log(f"7z command extraction failed: {e}", log_type='WARNING')

        return False, "No suitable extraction method available"


