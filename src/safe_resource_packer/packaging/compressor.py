"""
Compressor - 7z compression functionality (py7zr removed)

Handles compression of loose files and final package assembly using 7z CLI only.
Provides reliable compression with 7z command-line tool and ZIP fallback.
"""

import os
import subprocess
import shutil
import zipfile
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from ..utils import log


class Compressor:
    """Handles 7z compression for loose files and final packages using 7z CLI only."""

    def __init__(self, compression_level: int = 5):
        """
        Initialize compressor with 7z CLI only (py7zr removed).

        Args:
            compression_level: 7z compression level (0-9)
        """
        self.compression_level = max(0, min(9, compression_level))
        self.current_compression_tool = "Unknown"
        self.methods_tried = []

    def compress_files(self,
                      files: List[str],
                      archive_path: str,
                      base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Compress list of files into 7z archive using 7z CLI only.

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
        
        # Log which compression tool will be used
        self._log_compression_tool_selection()

        # PERFORMANCE OPTIMIZATION: Use bulk compression for many files
        if len(files) > 50:  # Threshold for bulk compression
            log(f"Using bulk compression optimization for {len(files)} files", log_type='INFO')
            
            # For very large file sets, use even faster compression
            if len(files) > 2000:
                log(f"Large file set detected ({len(files)} files), using fast compression mode", log_type='INFO')
                # Temporarily reduce compression level for speed
                original_level = self.compression_level
                self.compression_level = min(2, self.compression_level)  # Force fast compression
                try:
                    result = self._compress_files_bulk(files, str(archive_path), base_dir)
                finally:
                    self.compression_level = original_level  # Restore original level
                return result
            else:
                return self._compress_files_bulk(files, str(archive_path), base_dir)

        # Try 7z command first (has built-in multithreading)
        try:
            success, message = self._compress_with_7z_command(files, str(archive_path), base_dir)
            if success:
                self.methods_tried.append(f"7z command ({self.current_compression_tool}) (success)")
                return True, message
            log(f"7z command compression failed: {message}", log_type='WARNING')
            self.methods_tried.append(f"7z command ({self.current_compression_tool}) (failed)")
        except Exception as e:
            log(f"7z command compression error: {e}", log_type='ERROR')
            self.methods_tried.append(f"7z command ({self.current_compression_tool}) (error)")
        
        # Try ZIP fallback
        try:
            self.current_compression_tool = "ZIP fallback (Python zipfile)"
            success, message = self._compress_with_zip_fallback(files, str(archive_path), base_dir)
            if success:
                self.methods_tried.append("ZIP fallback (success)")
                return True, message
            log(f"ZIP compression failed: {message}", log_type='ERROR')
            self.methods_tried.append("ZIP fallback (failed)")
        except Exception as e:
            log(f"ZIP compression error: {e}", log_type='ERROR')
            self.methods_tried.append("ZIP fallback (error)")

        # All methods failed
        methods_str = ", ".join(self.methods_tried)
        return False, f"All compression methods failed. Tried: {methods_str}"

    def compress_bulk_directory(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """
        Compress entire directory using 7z CLI only (py7zr removed).

        Args:
            source_dir: Directory to compress
            archive_path: Output path for 7z archive

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
            return False, f"Source directory not found: {source_dir}"

        log(f"Compressing directory: {source_dir} -> {archive_path}", log_type='INFO')
        
        # Create temporary staging directory for better control
        with tempfile.TemporaryDirectory(prefix="bulk_compress_") as temp_dir:
            # Copy directory to temp location for safe processing
            temp_source = os.path.join(temp_dir, "source")
            shutil.copytree(source_dir, temp_source)
            
            # Method 1: Try 7z command first (has built-in multithreading with -mmt=on)
            try:
                success, message = self._compress_directory_with_7z_command(temp_source, archive_path)
                if success:
                    return True, message
                log(f"7z command directory compression failed: {message}", log_type='WARNING')
            except Exception as e:
                log(f"7z command directory compression error: {e}", log_type='ERROR')
            
            # Method 2: ZIP fallback (should always work)
            try:
                log("Falling back to ZIP compression...", log_type='INFO')
                self.current_compression_tool = "ZIP fallback (Python zipfile)"
                success, message = self._compress_directory_with_zip_fallback(temp_source, archive_path)
                if success:
                    return True, message
                log(f"ZIP fallback failed: {message}", log_type='ERROR')
            except Exception as e:
                log(f"ZIP fallback error: {e}", log_type='ERROR')

        return False, "All bulk compression methods failed"

    def _compress_directory_with_7z_command(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """Compress directory using 7z command with multithreading."""
        sevenz_cmd = self._find_7z_command()
        if not sevenz_cmd:
            return False, "7z command not found"

        self.current_compression_tool = f"7z command (multithreaded): {sevenz_cmd}"
        log(f"Using compression tool: {self.current_compression_tool}", log_type='INFO')

        try:
            # Use 7z with multithreading enabled
            cmd = [
                sevenz_cmd, 'a', archive_path,
                f'-mx{self.compression_level}',
                '-mmt=on',  # Enable multithreading
                os.path.join(source_dir, '*')
            ]
            
            # Set up progress tracking if available
            try:
                from ..dynamic_progress import start_dynamic_progress, finish_dynamic_progress, is_dynamic_progress_enabled, set_dynamic_progress_current, update_dynamic_progress
                if is_dynamic_progress_enabled():
                    # Estimate file count for progress
                    total_files = sum(len(files) for _, _, files in os.walk(source_dir))
                    start_dynamic_progress("Compression", total_files, preserve_stats=True)
                    compression_progress_active = True
                else:
                    compression_progress_active = False
            except ImportError:
                compression_progress_active = False

            # Execute 7z command
            result = self._run_7z_with_progress(cmd, compression_progress_active)
            
            # Finish compression progress
            if compression_progress_active:
                finish_dynamic_progress()

            if result.returncode == 0:
                if os.path.exists(archive_path):
                    size_mb = os.path.getsize(archive_path) / (1024 * 1024)
                    log(f"7z compression completed ({size_mb:.1f}MB)", log_type='INFO')
                    return True, f"Directory compressed with 7z: {archive_path} ({size_mb:.1f}MB)"
                else:
                    return False, "7z completed but archive not found"
            else:
                return False, f"7z command failed: {result.stderr}"

        except Exception as e:
            return False, f"7z directory compression failed: {e}"

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
                cmd = [sevenz_cmd, 'a', os.path.abspath(archive_path), f'-mx{self.compression_level}', '-mmt=on']
                relative_files = []
                
                log(f"7z CLI: Using base directory: {base_dir}", log_type='INFO')
                for file_path in files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, base_dir)
                        relative_files.append(rel_path)
                        file_size = os.path.getsize(file_path)
                        log(f"7z CLI: Adding {os.path.basename(file_path)} ({file_size} bytes) -> {rel_path}", log_type='INFO')
                    else:
                        log(f"7z CLI: File not found: {file_path}", log_type='WARNING')
                        
                cmd.extend(relative_files)
                log(f"7z CLI command: {' '.join(cmd)}", log_type='INFO')

                # Execute from base directory
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=base_dir)
            else:
                # Use absolute paths
                cmd = [sevenz_cmd, 'a', archive_path, f'-mx{self.compression_level}', '-mmt=on']
                log(f"7z CLI: Using absolute paths (no base directory)", log_type='INFO')
                for file_path in files:
                    if os.path.exists(file_path):
                        cmd.append(file_path)
                        file_size = os.path.getsize(file_path)
                        log(f"7z CLI: Adding {os.path.basename(file_path)} ({file_size} bytes) -> absolute path", log_type='INFO')
                    else:
                        log(f"7z CLI: File not found: {file_path}", log_type='WARNING')

                log(f"7z CLI command: {' '.join(cmd)}", log_type='INFO')
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

    def _compress_with_zip_fallback(self,
                                   files: List[str],
                                   archive_path: str,
                                   base_dir: Optional[str]) -> Tuple[bool, str]:
        """Fallback compression using Python zipfile."""
        try:
            # Convert .7z to .zip for fallback
            if archive_path.lower().endswith('.7z'):
                zip_path = archive_path[:-3] + '.zip'
            else:
                zip_path = archive_path + '.zip'

            log(f"Using ZIP fallback compression: {zip_path}", log_type='INFO')

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        if base_dir:
                            arcname = os.path.relpath(file_path, base_dir)
                        else:
                            arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)

            return True, f"Archive created with ZIP fallback: {zip_path}"

        except Exception as e:
            return False, f"ZIP fallback compression failed: {e}"

    def _find_7z_command(self) -> Optional[str]:
        """Find 7z executable in PATH or common locations."""
        # Check PATH first
        for cmd in ['7z', '7za', '7zr']:
            if shutil.which(cmd):
                self.current_compression_tool = f"{cmd} (high-quality): {shutil.which(cmd)}"
                return cmd

        return None

    def _log_compression_tool_selection(self):
        """Log available compression tools and selection priority."""
        log("🔧 Compression Tool Detection:", log_type='INFO')
        
        # Check 7z command availability
        sevenz_cmd = self._find_7z_command()
        if sevenz_cmd:
            log(f"  ✅ 7z command available - HIGH QUALITY", log_type='INFO')
            log(f"     Tool: {self.current_compression_tool}", log_type='INFO')
        else:
            log("  ❌ 7z command not found", log_type='WARNING')
            if os.name == 'nt':  # Windows
                log("     Install 7-Zip from: https://www.7-zip.org/", log_type='INFO')
            else:
                log("     Install with: sudo apt install p7zip-full (Ubuntu/Debian)", log_type='INFO')
                log("     Or: sudo pacman -S p7zip (Arch Linux)", log_type='INFO')
        
        # Determine priority order (7z CLI first)
        if sevenz_cmd:
            log(f"  🎯 Will use: 7z command ({self.current_compression_tool}) - built-in multithreading", log_type='INFO')
        else:
            log("  ⚠️  Will use: ZIP fallback (slower, larger files)", log_type='WARNING')
        
        log("", log_type='INFO')  # Empty line for spacing

    def _run_7z_with_progress(self, cmd: List[str], progress_active: bool) -> subprocess.CompletedProcess:
        """Run 7z command with progress tracking if available."""
        if not progress_active:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Run with progress tracking
        try:
            from ..dynamic_progress import update_dynamic_progress
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Simple progress simulation (7z doesn't provide detailed progress)
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                update_dynamic_progress("Compressing...", "compressing", "", increment=False)
                time.sleep(1)
            
            stdout, stderr = process.communicate()
            return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            
        except ImportError:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    def _compress_files_bulk(self,
                            files: List[str],
                            archive_path: str,
                            base_dir: Optional[str]) -> Tuple[bool, str]:
        """Bulk compress many files efficiently using 7z CLI."""
        return self._compress_with_7z_command(files, archive_path, base_dir)

    def _compress_with_7z_listfile(self,
                                   sevenz_cmd: str,
                                   files: List[str],
                                   archive_path: str,
                                   base_dir: Optional[str]) -> Tuple[bool, str]:
        """Compress using 7z with file list (for many files)."""
        try:
            # Create temporary file list in a safe location
            listfile_path = os.path.join(tempfile.gettempdir(), f"7z_filelist_{int(time.time())}.txt")
            files_added = 0
            
            log(f"Creating file list for {len(files)} files: {listfile_path}", log_type='INFO')
            
            with open(listfile_path, 'w', encoding='utf-8') as f:
                for file_path in files:
                    if os.path.exists(file_path):
                        if base_dir:
                            try:
                                rel_path = os.path.relpath(file_path, base_dir)
                                # Ensure we don't have problematic paths
                                if not rel_path.startswith('..') and rel_path != '.':
                                    f.write(f"{rel_path}\n")
                                    files_added += 1
                                else:
                                    log(f"Skipping problematic relative path: {rel_path} (from {file_path})", log_type='WARNING')
                            except ValueError as e:
                                log(f"Cannot create relative path for {file_path}: {e}", log_type='WARNING')
                                # Fall back to absolute path
                                f.write(f"{file_path}\n")
                                files_added += 1
                        else:
                            f.write(f"{file_path}\n")
                            files_added += 1
                    else:
                        log(f"File not found for list: {file_path}", log_type='WARNING')

            log(f"File list created with {files_added} files", log_type='INFO')
            
            if files_added == 0:
                return False, "No valid files found for compression"

            # Build command with file list - use absolute paths for listfile
            listfile_abs = os.path.abspath(listfile_path)
            if base_dir and os.path.exists(base_dir):
                cmd = [sevenz_cmd, 'a', os.path.abspath(archive_path), f'-mx{self.compression_level}', '-mmt=on', f'@{listfile_abs}']
                log(f"7z listfile command (with base_dir): {' '.join(cmd[:6])}... (working dir: {base_dir})", log_type='INFO')
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=base_dir)
            else:
                cmd = [sevenz_cmd, 'a', os.path.abspath(archive_path), f'-mx{self.compression_level}', '-mmt=on', f'@{listfile_abs}']
                log(f"7z listfile command (no base_dir): {' '.join(cmd)}", log_type='INFO')
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            # Clean up file list
            try:
                os.remove(listfile_path)
            except:
                pass

            if result.returncode == 0:
                return True, f"Archive created with 7z (file list): {archive_path}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                log(f"7z stderr: {error_msg}", log_type='ERROR')
                log(f"7z stdout: {result.stdout.strip()}", log_type='DEBUG')
                return False, f"7z file list compression failed: {error_msg}"

        except Exception as e:
            return False, f"7z file list compression error: {e}"

    def _compress_directory_with_zip_fallback(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """Fallback directory compression using ZIP."""
        try:
            # Convert .7z to .zip for fallback
            if archive_path.lower().endswith('.7z'):
                zip_path = archive_path[:-3] + '.zip'
            else:
                zip_path = archive_path + '.zip'

            log(f"Using ZIP fallback for directory: {zip_path}", log_type='INFO')

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

            return True, f"Directory compressed with ZIP fallback: {zip_path}"

        except Exception as e:
            return False, f"ZIP directory compression failed: {e}"
