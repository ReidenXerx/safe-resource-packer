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

def _ensure_py7zr_available():
    """Ensure py7zr is available, install if missing."""
    try:
        import py7zr
        return True, py7zr
    except ImportError:
        log("py7zr not found, attempting automatic installation...", log_type='INFO')
        try:
            import subprocess
            import sys
            
            # Try to install py7zr
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'py7zr>=0.20.0'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                log("py7zr installed successfully, importing...", log_type='INFO')
                import py7zr
                return True, py7zr
            else:
                log(f"Failed to install py7zr: {result.stderr}", log_type='WARNING')
                return False, None
                
        except Exception as e:
            log(f"Error installing py7zr: {e}", log_type='WARNING')
            return False, None

# Try to get py7zr with automatic installation
PY7ZR_AVAILABLE, py7zr = _ensure_py7zr_available()

if not PY7ZR_AVAILABLE:
    log("py7zr not available, falling back to command-line 7z", log_type='WARNING')
    py7zr = None


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
        self._py7zr_install_attempted = False
        self.current_compression_tool = None  # Track which tool we're using

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

        # Try different compression methods (for smaller file counts)
        # Try py7zr first (with automatic installation if needed)
        if PY7ZR_AVAILABLE or self._try_install_py7zr():
            try:
                success, message = self._compress_with_py7zr(files, str(archive_path), base_dir)
                if success:
                    self.methods_tried.append("py7zr (success)")
                    return True, message
                log(f"py7zr compression failed: {message}", log_type='WARNING')
                self.methods_tried.append("py7zr (failed)")
            except Exception as e:
                log(f"py7zr compression error: {e}", log_type='ERROR')
                self.methods_tried.append("py7zr (error)")
        
        # Try 7z command
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

        return False, f"All compression methods failed. Tried: {self.methods_tried}\nLast tool attempted: {self.current_compression_tool or 'unknown'}"

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

    def _compress_files_bulk(self,
                           files: List[str],
                           archive_path: str,
                           base_dir: Optional[str]) -> Tuple[bool, str]:
        """
        PERFORMANCE OPTIMIZED: Create temporary folder structure and compress entire folder.
        
        This method dramatically improves performance by:
        1. Creating a temporary folder with proper game directory structure
        2. Copying all files to temp folder with correct relative paths  
        3. Compressing the entire temp folder in one operation
        
        This avoids the massive I/O overhead of adding files one-by-one to the archive.
        """
        import tempfile
        
        try:
            # Create temporary directory for staging files
            with tempfile.TemporaryDirectory(prefix="loose_package_") as temp_dir:
                log(f"Creating temporary file structure in: {temp_dir}", debug_only=True, log_type='INFO')
                
                # Copy all files to temporary directory with proper structure
                copied_count = 0
                for file_path in files:
                    if not os.path.exists(file_path):
                        log(f"Skipping missing file: {file_path}", log_type='WARNING')
                        continue
                    
                    # Calculate relative path for proper game structure
                    if base_dir:
                        rel_path = os.path.relpath(file_path, base_dir)
                    else:
                        rel_path = self._extract_data_relative_path(file_path)
                    
                    # Create destination path in temp directory
                    dest_path = os.path.join(temp_dir, rel_path)
                    dest_dir = os.path.dirname(dest_path)
                    
                    # Create destination directory if needed
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # Copy file to temp structure
                    shutil.copy2(file_path, dest_path)
                    copied_count += 1
                    
                    if copied_count % 100 == 0:  # Progress logging every 100 files
                        log(f"Staged {copied_count}/{len(files)} files...", debug_only=True, log_type='INFO')
                
                log(f"Successfully staged {copied_count} files in temp directory", log_type='INFO')
                
                # Now compress the entire temp directory in one operation using direct methods
                # Use compress_directory but avoid recursion by using the internal methods directly
                log(f"Compressing temp directory to final archive: {archive_path}", log_type='INFO')
                
                # Try the compression methods directly without going through compress_files again
                # Method 1: Try py7zr (with automatic installation if needed)
                if PY7ZR_AVAILABLE or self._try_install_py7zr():
                    try:
                        success, message = self._compress_directory_with_py7zr(temp_dir, archive_path)
                        if success:
                            return True, message
                        log(f"py7zr directory compression failed: {message}", log_type='WARNING')
                    except Exception as e:
                        log(f"py7zr directory compression error: {e}", log_type='ERROR')
                
                # Method 2: Try 7z command
                try:
                    success, message = self._compress_directory_with_7z_command(temp_dir, archive_path)
                    if success:
                        return True, message
                    log(f"7z command directory compression failed: {message}", log_type='WARNING')
                except Exception as e:
                    log(f"7z command directory compression error: {e}", log_type='ERROR')
                
                # Method 3: ZIP fallback (should always work)
                try:
                    log("Falling back to ZIP compression...", log_type='INFO')
                    self.current_compression_tool = "ZIP fallback (Python zipfile)"
                    success, message = self._compress_directory_with_zip_fallback(temp_dir, archive_path)
                    if success:
                        return True, message
                    log(f"ZIP fallback failed: {message}", log_type='ERROR')
                except Exception as e:
                    log(f"ZIP fallback error: {e}", log_type='ERROR')
                
                return False, "All directory compression methods failed (py7zr, 7z command, and ZIP)"
                
        except Exception as e:
            return False, f"Bulk compression failed: {e}"

    def _try_install_py7zr(self) -> bool:
        """Try to install py7zr if not already attempted."""
        global PY7ZR_AVAILABLE, py7zr
        
        if self._py7zr_install_attempted or PY7ZR_AVAILABLE:
            return PY7ZR_AVAILABLE
            
        self._py7zr_install_attempted = True
        log("py7zr not found - better compression performance available with py7zr", log_type='INFO')
        
        try:
            import subprocess
            import sys
            import platform
            
            # Check operating system and provide specific guidance
            system = platform.system()
            if system == "Linux":
                try:
                    with open("/etc/os-release", "r") as f:
                        os_info = f.read()
                    if "arch" in os_info.lower() or "manjaro" in os_info.lower():
                        log("Arch Linux detected. Install py7zr with: sudo pacman -S python-py7zr", log_type='INFO')
                        return False
                except:
                    pass
            elif system == "Windows":
                log("Windows detected. py7zr should install automatically via pip...", log_type='INFO')
            
            # Try different installation methods based on platform
            install_commands = []
            
            if system == "Windows":
                # Windows-specific installation attempts
                install_commands = [
                    [sys.executable, '-m', 'pip', 'install', 'py7zr>=0.20.0', '--quiet'],
                    ['py', '-m', 'pip', 'install', 'py7zr>=0.20.0', '--quiet'],  # Python Launcher
                    [sys.executable, '-m', 'pip', 'install', '--user', 'py7zr>=0.20.0', '--quiet']  # User install
                ]
            else:
                # Linux/Mac installation
                install_commands = [
                    [sys.executable, '-m', 'pip', 'install', 'py7zr>=0.20.0', '--quiet']
                ]
            
            result = None
            for cmd in install_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        break  # Success, stop trying other methods
                    else:
                        log(f"Installation attempt failed with: {' '.join(cmd)}", debug_only=True, log_type='INFO')
                except Exception as e:
                    log(f"Command failed: {e}", debug_only=True, log_type='WARNING')
                    continue
            
            # Use the last result for error handling
            if result is None:
                return False
            
            if result.returncode == 0:
                try:
                    import py7zr as py7zr_module
                    PY7ZR_AVAILABLE = True
                    py7zr = py7zr_module
                    log("py7zr installed successfully! Using py7zr for optimal compression.", log_type='INFO')
                    return True
                except ImportError as e:
                    log(f"py7zr installed but import failed: {e}", log_type='WARNING')
                    return False
            else:
                # Check for different types of installation failures
                stderr_text = result.stderr.lower()
                
                if "externally-managed-environment" in stderr_text:
                    log("System-managed Python environment detected.", log_type='INFO')
                    log("For optimal compression, install py7zr using your system package manager:", log_type='INFO')
                    log("  • Arch/Manjaro: sudo pacman -S python-py7zr", log_type='INFO')
                    log("  • Ubuntu/Debian: sudo apt install python3-py7zr", log_type='INFO')
                    log("  • Or use virtual environment: python -m venv venv", log_type='INFO')
                elif "permission denied" in stderr_text and system == "Windows":
                    log("Permission error on Windows. Try one of these solutions:", log_type='INFO')
                    log("  • Run as Administrator: Right-click Command Prompt → 'Run as administrator'", log_type='INFO')
                    log("  • Install for user only: pip install --user py7zr>=0.20.0", log_type='INFO')
                    log("  • Use Python launcher: py -m pip install py7zr>=0.20.0", log_type='INFO')
                elif "network" in stderr_text or "timeout" in stderr_text or "connection" in stderr_text:
                    log("Network connection issue detected.", log_type='INFO')
                    log("Please check your internet connection and try again.", log_type='INFO')
                    if system == "Windows":
                        log("Windows users can also try: py -m pip install py7zr>=0.20.0", log_type='INFO')
                else:
                    log(f"py7zr installation failed: {result.stderr[:200]}...", log_type='WARNING')
                    if system == "Windows":
                        log("Windows troubleshooting:", log_type='INFO')
                        log("  • Try: py -m pip install py7zr>=0.20.0", log_type='INFO')
                        log("  • Or: pip install --user py7zr>=0.20.0", log_type='INFO')
                        log("  • Or run Command Prompt as Administrator", log_type='INFO')
                
                return False
                
        except Exception as e:
            log(f"Could not install py7zr: {e}", log_type='WARNING')
            return False

    def _compress_directory_with_py7zr(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """Compress directory using py7zr library with progress tracking."""
        if not PY7ZR_AVAILABLE:
            return False, "py7zr library not available"
        
        self.current_compression_tool = "py7zr (Python library - high quality)"
        log(f"Using compression tool: {self.current_compression_tool}", log_type='INFO')
        
        try:
            # Count files for progress tracking
            total_files = 0
            for root, dirs, files in os.walk(source_dir):
                total_files += len(files)
            
            log(f"py7zr compressing {total_files} files...", log_type='INFO')
            
            filters = [{"id": py7zr.FILTER_LZMA2, "preset": self.compression_level}]
            with py7zr.SevenZipFile(archive_path, 'w', filters=filters) as archive:
                # Use writeall but add some progress feedback
                import time
                start_time = time.time()
                archive.writeall(source_dir, ".")
                elapsed = time.time() - start_time
                
            if os.path.exists(archive_path):
                size_mb = os.path.getsize(archive_path) / (1024 * 1024)
                log(f"py7zr compression completed in {elapsed:.1f}s ({size_mb:.1f}MB)", log_type='INFO')
                return True, f"Directory compressed with py7zr: {archive_path} ({size_mb:.1f}MB)"
            else:
                return False, "py7zr completed but archive not found"
                
        except Exception as e:
            return False, f"py7zr directory compression failed: {e}"

    def _compress_directory_with_7z_command(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """Compress directory using command-line 7z tool with progress monitoring."""
        sevenz_cmd = self._find_7z_command()
        if not sevenz_cmd:
            return False, "7z command not found"
        
        # Log which tool we're using
        log(f"Using compression tool: {self.current_compression_tool}", log_type='INFO')
        
        try:
            # Use faster compression for large directories (mx3 instead of mx5+)
            # This significantly speeds up compression with minimal size penalty
            fast_compression = max(1, min(3, self.compression_level))
            
            cmd = [
                sevenz_cmd, 'a', archive_path, 
                f'-mx{fast_compression}',  # Faster compression
                '-mmt=on',  # Multi-threading
                '-ms=on',   # Solid mode for better compression
                f'{source_dir}/*'
            ]
            
            log(f"Starting 7z compression (level {fast_compression}, multi-threaded)...", log_type='INFO')
            
            # Run compression with progress monitoring
            result = self._run_7z_with_progress(cmd, source_dir)
            
            if result.returncode == 0:
                if os.path.exists(archive_path):
                    size_mb = os.path.getsize(archive_path) / (1024 * 1024)
                    return True, f"Directory compressed with 7z: {archive_path} ({size_mb:.1f}MB)"
                else:
                    return False, "7z completed but archive not found"
            else:
                return False, f"7z directory compression failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "7z compression timed out (30+ minutes)"
        except Exception as e:
            return False, f"7z directory compression failed: {e}"

    def _compress_directory_with_zip_fallback(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """Fallback directory compression using ZIP format with progress."""
        try:
            zip_path = archive_path.replace('.7z', '.zip')
            
            # Count total files for progress
            log("Counting files for ZIP compression...", log_type='INFO')
            total_files = 0
            for root, dirs, files in os.walk(source_dir):
                total_files += len(files)
            
            log(f"Using ZIP compression for {total_files} files (faster compression level)", log_type='INFO')
            
            # Use very fast compression for large file sets
            compression_level = 1 if total_files > 2000 else min(self.compression_level, 4)
            log(f"ZIP compression level: {compression_level} (optimized for speed)", log_type='INFO')
            
            processed = 0
            last_progress_time = 0
            import time
            start_time = time.time()
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_dir)
                            zipf.write(file_path, arcname)
                            processed += 1
                            
                            # Progress every 250 files OR every 10 seconds
                            current_time = time.time()
                            if (processed % 250 == 0) or (current_time - last_progress_time > 10):
                                percent = (processed * 100) // total_files
                                elapsed = current_time - start_time
                                rate = processed / elapsed if elapsed > 0 else 0
                                eta_seconds = (total_files - processed) / rate if rate > 0 else 0
                                eta_minutes = int(eta_seconds // 60)
                                
                                log(f"ZIP progress: {processed}/{total_files} files ({percent}%) - {rate:.0f} files/sec - ETA: {eta_minutes}m", log_type='INFO')
                                last_progress_time = current_time
                                
                        except Exception as file_error:
                            log(f"Skipping file {file_path}: {file_error}", log_type='WARNING')
                            continue
            
            if os.path.exists(zip_path):
                size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                elapsed = time.time() - start_time
                log(f"ZIP compression completed in {elapsed:.1f}s", log_type='INFO')
                return True, f"Directory compressed with ZIP: {zip_path} ({size_mb:.1f}MB)"
            else:
                return False, "ZIP file was not created"
                
        except Exception as e:
            import traceback
            log(f"ZIP compression error: {traceback.format_exc()}", log_type='ERROR')
            return False, f"ZIP directory compression failed: {e}"

    def _run_7z_with_progress(self, cmd: List[str], source_dir: str):
        """Run 7z command with enhanced progress monitoring and percentage tracking."""
        import threading
        import time
        
        # Count files for progress estimation
        file_count = 0
        for root, dirs, files in os.walk(source_dir):
            file_count += len(files)
        
        log(f"Compressing {file_count} files, this may take several minutes...", log_type='INFO')
        
        # Start the process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Enhanced progress monitoring thread
        start_time = time.time()
        
        def progress_monitor():
            last_update = 0
            
            while process.poll() is None:
                elapsed = time.time() - start_time
                
                # Show progress updates more frequently with percentage estimation
                if elapsed - last_update >= 15:  # Every 15 seconds
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)
                    
                    # Rough percentage estimation based on elapsed time
                    # This is a heuristic - actual progress varies by file sizes
                    if elapsed < 60:
                        estimated_percent = min(25, int(elapsed * 0.4))  # 0-25% in first minute
                    elif elapsed < 300:  # 5 minutes
                        estimated_percent = min(70, 25 + int((elapsed - 60) * 0.18))  # 25-70% in next 4 minutes
                    else:
                        estimated_percent = min(95, 70 + int((elapsed - 300) * 0.01))  # 70-95% after 5 minutes
                    
                    log(f"7z compression progress: ~{estimated_percent}% complete ({minutes}m {seconds}s elapsed)", log_type='INFO')
                    last_update = elapsed
                    
                time.sleep(5)  # Check every 5 seconds
        
        # Start progress monitoring in background
        progress_thread = threading.Thread(target=progress_monitor, daemon=True)
        progress_thread.start()
        
        # Wait for completion with extended timeout (30 minutes for large files)
        try:
            stdout, stderr = process.communicate(timeout=1800)  # 30 minute timeout
            
            # Final progress update
            elapsed_total = time.time() - start_time
            log(f"7z compression completed: 100% ({int(elapsed_total//60)}m {int(elapsed_total%60)}s total)", log_type='INFO')
            
            # Create result object similar to subprocess.run
            class CompletedProcess:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            return CompletedProcess(process.returncode, stdout, stderr)
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise

    def _compress_with_py7zr(self,
                            files: List[str],
                            archive_path: str,
                            base_dir: Optional[str]) -> Tuple[bool, str]:
        """Compress using py7zr library with progress tracking."""

        if not PY7ZR_AVAILABLE:
            return False, "py7zr library not available"

        self.current_compression_tool = "py7zr (Python library - high quality)"
        log(f"Using compression tool: {self.current_compression_tool}", log_type='INFO')

        try:
            # Create filters for compression
            filters = [{"id": py7zr.FILTER_LZMA2, "preset": self.compression_level}]
            
            total_files = len(files)
            processed_files = 0
            
            with py7zr.SevenZipFile(archive_path, 'w', filters=filters) as archive:
                for i, file_path in enumerate(files, 1):
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
                    processed_files += 1
                    
                    # Progress reporting every 100 files or 10%
                    if (i % 100 == 0) or (i % max(1, total_files // 10) == 0):
                        percent = (i * 100) // total_files
                        log(f"py7zr compression progress: {i}/{total_files} files ({percent}%)", log_type='INFO')

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
        """Find best 7z executable, prioritizing quality tools over Windows defaults."""
        import platform
        
        # PRIORITY 1: High-quality 7z installations (avoid Windows default crap)
        high_quality_paths = []
        
        if platform.system() == 'Windows':
            # Prefer full 7-Zip installation over Windows built-in
            high_quality_paths = [
                "C:/Program Files/7-Zip/7z.exe",
                "C:/Program Files (x86)/7-Zip/7z.exe",
            ]
        else:
            # Linux/Mac - prefer system packages
            high_quality_paths = [
                "/usr/bin/7z",
                "/usr/local/bin/7z",
                "/opt/7z/7z"
            ]
        
        # Check high-quality installations first
        for path in high_quality_paths:
            if os.path.exists(path):
                self.current_compression_tool = f"7z (high-quality): {path}"
                return path
        
        # PRIORITY 2: Check PATH for proper 7z tools (but be careful on Windows)
        path_commands = ['7z', '7za', '7zr']
        
        # On Windows, be more selective about PATH commands
        if platform.system() == 'Windows':
            # Add .exe versions but prioritize 7za (7-Zip standalone)
            path_commands = ['7za.exe', '7z.exe', '7za', '7zr.exe', '7zr', '7z']
        
        for cmd in path_commands:
            found_path = shutil.which(cmd)
            if found_path:
                # On Windows, verify it's not the crappy built-in one
                if platform.system() == 'Windows':
                    # Check if it's in System32 (usually the bad one)
                    if 'system32' in found_path.lower() or 'syswow64' in found_path.lower():
                        log(f"Skipping Windows built-in 7z at: {found_path} (poor performance)", 
                            debug_only=True, log_type='WARNING')
                        continue
                
                self.current_compression_tool = f"7z (PATH): {found_path}"
                return found_path
        
        # PRIORITY 3: Last resort - even Windows built-in if nothing else
        if platform.system() == 'Windows':
            fallback_paths = [
                "C:/Windows/System32/tar.exe",  # Windows 10+ has tar with 7z support
            ]
            for path in fallback_paths:
                if os.path.exists(path):
                    log(f"Using fallback compression tool: {path} (may be slower)", log_type='WARNING')
                    self.current_compression_tool = f"fallback: {path}"
                    return path
        
        self.current_compression_tool = "none found"
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
                # Only log path extraction for debugging if needed (commented out to reduce spam)
                # log(f"Extracted Data path: {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # If no game directory found, look for common patterns
        for i, part in enumerate(path_parts):
            part_lower = part.lower()
            # Check for Data directory itself
            if part_lower == 'data' and i < len(path_parts) - 1:
                # Return everything after 'data' directory
                data_relative = '/'.join(path_parts[i+1:])
                # log(f"Found Data folder: {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # Fallback: use the last 2-3 path components to preserve some structure
        if len(path_parts) >= 2:
            # Try to preserve at least directory/filename structure
            fallback_path = '/'.join(path_parts[-2:])
            # Only log fallback paths occasionally to avoid spam
            # log(f"Fallback Data path: {file_path} → {fallback_path}", debug_only=True, log_type='WARNING')
            return fallback_path
        else:
            # Last resort: just the filename
            filename = os.path.basename(file_path)
            # log(f"Using filename only: {file_path} → {filename}", debug_only=True, log_type='WARNING')
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
    
    def _log_compression_tool_selection(self):
        """Log which compression tools are available and which will be used."""
        import platform
        
        log("🔧 Compression Tool Detection:", log_type='INFO')
        
        # Check py7zr availability
        if PY7ZR_AVAILABLE:
            log("  ✅ py7zr (Python library) - HIGH QUALITY, FAST", log_type='INFO')
        else:
            log("  ❌ py7zr not available - install with: pip install py7zr>=0.20.0", log_type='WARNING')
        
        # Check 7z command availability
        sevenz_cmd = self._find_7z_command()
        if sevenz_cmd:
            quality = "HIGH QUALITY" if "high-quality" in (self.current_compression_tool or "") else "STANDARD"
            log(f"  ✅ 7z command available - {quality}", log_type='INFO')
            log(f"     Tool: {self.current_compression_tool}", log_type='INFO')
        else:
            log("  ❌ 7z command not found", log_type='WARNING')
            if platform.system() == 'Windows':
                log("     Install 7-Zip from: https://www.7-zip.org/", log_type='INFO')
            else:
                log("     Install with: sudo apt install p7zip-full (Ubuntu/Debian)", log_type='INFO')
                log("     Or: sudo pacman -S p7zip (Arch Linux)", log_type='INFO')
        
        # Determine priority order
        if PY7ZR_AVAILABLE:
            log("  🎯 Will use: py7zr (best quality and speed)", log_type='INFO')
        elif sevenz_cmd:
            log(f"  🎯 Will use: 7z command ({self.current_compression_tool})", log_type='INFO')
        else:
            log("  ⚠️  Will use: ZIP fallback (slower, larger files)", log_type='WARNING')
        
        log("" , log_type='INFO')  # Empty line for spacing

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


