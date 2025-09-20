"""
Unified 7z CLI Compression Service

A single, simple, reliable compression service that handles ALL compression needs.
No more scattered compression logic - everything goes through this service.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from ..dynamic_progress import log


class CompressionService:
    """Unified 7z CLI compression service - handles ALL compression needs."""

    def __init__(self, compression_level: int = 3):
        """
        Initialize compression service.
        
        Args:
            compression_level: 7z compression level (0-9)
        """
        self.compression_level = max(0, min(9, compression_level))
        self.sevenz_cmd = self._find_7z_command()
        
    def _find_7z_command(self) -> Optional[str]:
        """Find 7z command executable."""
        # Try different possible 7z command names in order of preference
        # Accept both 7z CLI and NanaZip (they're both valid)
        possible_commands = ['7z', '7za', '7zz']
        
        for cmd in possible_commands:
            if shutil.which(cmd):
                # Verify this is a valid 7z-compatible command
                try:
                    result = subprocess.run([cmd, '--help'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        help_text = result.stdout.lower()
                        # Accept both 7z CLI and NanaZip
                        if ('7-zip' in help_text or 'igor pavlov' in help_text or 
                            'nanazip' in help_text or 'm2-team' in help_text):
                            log(f"Found 7z-compatible command: {cmd}", log_type='DEBUG')
                            return cmd
                        else:
                            log(f"Found {cmd} but couldn't verify it's 7z-compatible", log_type='WARNING')
                            continue
                except Exception as e:
                    log(f"Error checking {cmd}: {e}", log_type='WARNING')
                    continue
        
        # Check what's available and provide helpful error message
        available_commands = []
        for cmd in ['7z', '7za', '7zz']:
            if shutil.which(cmd):
                available_commands.append(cmd)
        
        if available_commands:
            log(f"Available commands found but none are verified 7z-compatible: {available_commands}", log_type='WARNING')
            log("Please install 7z CLI or NanaZip: https://www.7-zip.org/download.html or https://github.com/M2Team/NanaZip", log_type='WARNING')
        else:
            log("No compression commands found in PATH", log_type='WARNING')
            log("Please install 7z CLI or NanaZip: https://www.7-zip.org/download.html or https://github.com/M2Team/NanaZip", log_type='WARNING')
                
        return None
        
    def is_available(self) -> bool:
        """Check if 7z CLI is available."""
        return self.sevenz_cmd is not None
        
    def _is_nanazip(self) -> bool:
        """Check if we're using NanaZip."""
        if not self.sevenz_cmd:
            return False
        try:
            result = subprocess.run([self.sevenz_cmd, '--help'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                help_text = result.stdout.lower()
                return 'nanazip' in help_text or 'm2-team' in help_text
        except Exception:
            pass
        return False
        
    def _test_mmt_parameter(self) -> bool:
        """Test if the current 7z command supports -mmt parameter."""
        if not self.sevenz_cmd:
            return False
        
        # NanaZip doesn't support -mmt parameter, so skip it
        if self._is_nanazip():
            return False
            
        try:
            # Test with a simple command that uses -mmt
            result = subprocess.run([self.sevenz_cmd, 'a', '-mmt=on', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            # If it doesn't error out, the parameter is supported
            return result.returncode == 0
        except Exception:
            return False
        
    def compress_directory(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """
        Compress entire directory to 7z archive.
        SIMPLE: 7z a archive.7z directory/*
        
        Args:
            source_dir: Directory to compress
            archive_path: Output archive path
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"
            
        # Ensure .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = str(Path(archive_path).with_suffix('.7z'))
            
        try:
            # Method 1: Simple directory compression - use directory path without wildcard
            # On Windows, use forward slashes for 7z compatibility
            source_path = os.path.abspath(source_dir)
            if os.name == 'nt':  # Windows
                source_path = source_path.replace('\\', '/')
                
            # Build command with adaptive parameters
            cmd = [
                self.sevenz_cmd, 'a', 
                os.path.abspath(archive_path),
                f'-mx{self.compression_level}',
                source_path
            ]
            
            # Add multithreading parameter if supported
            is_nanazip = self._is_nanazip()
            supports_mmt = self._test_mmt_parameter()
            
            log(f"Detected NanaZip: {is_nanazip}, Supports -mmt: {supports_mmt}", log_type='DEBUG')
            
            if supports_mmt:
                cmd.insert(-1, '-mmt=on')  # Insert before source_path
                log(f"Using multithreading parameter (-mmt=on)", log_type='DEBUG')
            else:
                log(f"Multithreading parameter not supported, skipping", log_type='DEBUG')
                
            # Add NanaZip-specific parameters if needed
            if is_nanazip:
                cmd.insert(-1, '-y')  # Assume Yes on all queries
                log(f"Using NanaZip-specific parameters", log_type='DEBUG')
            else:
                log(f"Using standard 7z parameters", log_type='DEBUG')
            
            # On Windows, try a different approach first
            if os.name == 'nt':
                # Method 1.5: Windows-specific approach - change to source directory and use relative paths
                log("Trying Windows-specific directory compression...", log_type='DEBUG')
                original_cwd = os.getcwd()
                try:
                    os.chdir(source_dir)
                    # Build Windows command with adaptive parameters
                    cmd_windows = [
                        self.sevenz_cmd, 'a', 
                        os.path.abspath(archive_path),
                        f'-mx{self.compression_level}',
                        '.'  # Current directory
                    ]
                    
                    # Add multithreading parameter if supported
                    is_nanazip = self._is_nanazip()
                    supports_mmt = self._test_mmt_parameter()
                    
                    if supports_mmt:
                        cmd_windows.insert(-1, '-mmt=on')  # Insert before '.'
                        
                    # Add NanaZip-specific parameters if needed
                    if is_nanazip:
                        cmd_windows.insert(-1, '-y')  # Assume Yes on all queries
                    
                    # Log the Windows-specific command
                    log(f"Executing Windows 7z command: {' '.join(cmd_windows)}", log_type='DEBUG')
                    log(f"Changed to directory: {os.getcwd()}", log_type='DEBUG')
                    
                    result_windows = subprocess.run(cmd_windows, capture_output=True, text=True, timeout=3600)
                    
                    # Log detailed results
                    log(f"Windows 7z return code: {result_windows.returncode}", log_type='DEBUG')
                    if result_windows.stdout:
                        log(f"Windows 7z stdout: {result_windows.stdout}", log_type='DEBUG')
                    if result_windows.stderr:
                        log(f"Windows 7z stderr: {result_windows.stderr}", log_type='DEBUG')
                    
                    if result_windows.returncode != 0:
                        log(f"Windows method failed (code {result_windows.returncode}), trying standard method...", log_type='DEBUG')
                    
                    if result_windows.returncode == 0:
                        archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
                        return True, f"Directory compressed successfully (Windows method): {archive_path} ({archive_size:,} bytes)"
                    else:
                        log(f"Windows method failed, trying standard method...", log_type='DEBUG')
                finally:
                    os.chdir(original_cwd)
            
            # Check for potential issues with large directories (quietly)
            total_size = 0
            file_count = 0
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            log(f"Compressing {file_count} files ({total_size / (1024*1024):.1f} MB)", log_type='INFO')
            
            # Check if we're dealing with a very large directory
            if total_size > 5 * 1024 * 1024 * 1024:  # 5GB
                log(f"Large directory detected ({total_size / (1024*1024*1024):.1f} GB), using file-by-file method", log_type='INFO')
                # Skip to file-by-file method for very large directories
                files_to_compress = []
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        files_to_compress.append(os.path.join(root, file))
                return self.compress_files(files_to_compress, archive_path)
            
            # Log the exact command being executed
            log(f"Executing 7z command: {' '.join(cmd)}", log_type='DEBUG')
            log(f"Working directory: {os.getcwd()}", log_type='DEBUG')
            log(f"Source path: {source_path}", log_type='DEBUG')
            log(f"Archive path: {archive_path}", log_type='DEBUG')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            # Log detailed results
            log(f"7z return code: {result.returncode}", log_type='DEBUG')
            if result.stdout:
                log(f"7z stdout: {result.stdout}", log_type='DEBUG')
            if result.stderr:
                log(f"7z stderr: {result.stderr}", log_type='DEBUG')
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                stdout_msg = result.stdout.strip() if result.stdout else "No stdout"
                log(f"7z command failed with return code {result.returncode}", log_type='ERROR')
                log(f"Command: {' '.join(cmd)}", log_type='ERROR')
                log(f"Error: {error_msg}", log_type='ERROR')
                if stdout_msg:
                    log(f"Output: {stdout_msg}", log_type='ERROR')
            
            if result.returncode == 0:
                archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
                return True, f"Directory compressed successfully: {archive_path} ({archive_size:,} bytes)"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                
                # Method 2: Fallback - try with individual file listing
                log("Trying fallback method with file listing...", log_type='DEBUG')
                
                # Get all files in the directory
                files_to_compress = []
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        files_to_compress.append(os.path.join(root, file))
                
                log(f"Using file-by-file method for {len(files_to_compress)} files", log_type='INFO')
                
                if not files_to_compress:
                    return False, f"7z compression failed: {error_msg} (no files found in directory)"
                
                # Use the compress_files method instead
                log(f"Using file-by-file compression method...", log_type='DEBUG')
                return self.compress_files(files_to_compress, archive_path)
                
        except subprocess.TimeoutExpired:
            return False, "7z compression timed out (>60 minutes)"
        except Exception as e:
            return False, f"7z compression error: {e}"
            
    def compress_directory_with_folder_name(self, source_dir: str, archive_path: str, folder_name: str) -> Tuple[bool, str]:
        """
        Compress directory contents with a custom folder name inside the archive.
        
        Args:
            source_dir: Directory to compress
            archive_path: Output archive path
            folder_name: Name of the folder inside the archive
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"
            
        # Ensure .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = str(Path(archive_path).with_suffix('.7z'))
            
        try:
            # Directly compress the source directory contents without creating a custom folder
            # This puts files at the root level of the archive, just like how plugins are handled
            log(f"📦 Compressing directory contents directly (no custom folder): {source_dir}", log_type='INFO')
            
            # Verify what's in the source directory before compression
            staging_contents = []
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), source_dir)
                    staging_contents.append(rel_path)
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), source_dir)
                    staging_contents.append(rel_path + '/')
                    
            log(f"📦 Source directory contents to compress: {staging_contents[:20]}{'...' if len(staging_contents) > 20 else ''}", log_type='INFO')
            
            # Compress the source directory directly using the contents compression method
            return self._compress_directory_contents_directly(source_dir, archive_path)
                
        except Exception as e:
            return False, f"Directory compression with custom folder failed: {e}"
            
    def _compress_directory_contents_directly(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """
        Compress directory contents directly without creating a wrapper folder.
        Files will appear at the root level of the archive.
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"
            
        # Ensure .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = str(Path(archive_path).with_suffix('.7z'))
            
        try:
            # Change to source directory and compress all contents
            original_cwd = os.getcwd()
            os.chdir(source_dir)
            
            try:
                # Build command to compress all contents of current directory
                cmd = [
                    self.sevenz_cmd, 'a', 
                    os.path.abspath(archive_path),
                    f'-mx{self.compression_level}',
                    '*'  # Compress all contents
                ]
                
                # Add multithreading parameter if supported
                is_nanazip = self._is_nanazip()
                supports_mmt = self._test_mmt_parameter()
                
                if supports_mmt:
                    cmd.insert(-1, '-mmt=on')
                    
                # Add NanaZip-specific parameters if needed
                if is_nanazip:
                    cmd.insert(-1, '-y')
                
                # Log command
                log(f"Executing 7z command (direct contents): {' '.join(cmd)}", log_type='DEBUG')
                log(f"Working directory: {os.getcwd()}", log_type='DEBUG')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
                
                # Log results
                log(f"7z return code: {result.returncode}", log_type='DEBUG')
                if result.stdout:
                    log(f"7z stdout: {result.stdout}", log_type='DEBUG')
                if result.stderr:
                    log(f"7z stderr: {result.stderr}", log_type='DEBUG')
                
                if result.returncode == 0:
                    archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
                    return True, f"Directory contents compressed successfully: {archive_path} ({archive_size:,} bytes)"
                else:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                    return False, f"7z compression failed: {error_msg}"
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False, f"Directory contents compression failed: {e}"
            
    def _compress_directory_direct(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """
        Direct directory compression without fallback methods (to avoid loops).
        Used internally by compress_files method.
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"
            
        # Ensure .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = str(Path(archive_path).with_suffix('.7z'))
            
        try:
            # On Windows, use forward slashes for 7z compatibility
            source_path = os.path.abspath(source_dir)
            if os.name == 'nt':  # Windows
                source_path = source_path.replace('\\', '/')
                
            # Build command with adaptive parameters
            cmd = [
                self.sevenz_cmd, 'a', 
                os.path.abspath(archive_path),
                f'-mx{self.compression_level}',
                source_path
            ]
            
            # Add multithreading parameter if supported
            is_nanazip = self._is_nanazip()
            supports_mmt = self._test_mmt_parameter()
            
            if supports_mmt:
                cmd.insert(-1, '-mmt=on')  # Insert before source_path
                
            # Add NanaZip-specific parameters if needed
            if is_nanazip:
                cmd.insert(-1, '-y')  # Assume Yes on all queries
            
            # Log the exact command being executed
            log(f"Executing 7z command: {' '.join(cmd)}", log_type='DEBUG')
            log(f"Working directory: {os.getcwd()}", log_type='DEBUG')
            log(f"Source path: {source_path}", log_type='DEBUG')
            log(f"Archive path: {archive_path}", log_type='DEBUG')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            # Log detailed results
            log(f"7z return code: {result.returncode}", log_type='DEBUG')
            if result.stdout:
                log(f"7z stdout: {result.stdout}", log_type='DEBUG')
            if result.stderr:
                log(f"7z stderr: {result.stderr}", log_type='DEBUG')
            
            if result.returncode == 0:
                archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
                return True, f"Directory compressed successfully: {archive_path} ({archive_size:,} bytes)"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                stdout_msg = result.stdout.strip() if result.stdout else "No stdout"
                log(f"7z command failed with return code {result.returncode}", log_type='ERROR')
                log(f"Command: {' '.join(cmd)}", log_type='ERROR')
                log(f"Error: {error_msg}", log_type='ERROR')
                if stdout_msg:
                    log(f"Output: {stdout_msg}", log_type='ERROR')
                return False, f"7z compression failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "7z compression timed out (>60 minutes)"
        except Exception as e:
            return False, f"7z compression error: {e}"
            
    def compress_files(self, files: List[str], archive_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Compress list of files to 7z archive.
        SIMPLE: Copy files to temp directory, then compress directory.
        
        Args:
            files: List of file paths to compress
            archive_path: Output archive path
            base_dir: Base directory for maintaining relative structure (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not files:
            return False, "No files provided for compression"
            
        # Ensure .7z extension
        if not archive_path.lower().endswith('.7z'):
            archive_path = str(Path(archive_path).with_suffix('.7z'))
            
        # Use temp directory approach - ALWAYS works
        # Use shorter prefix on Windows to avoid path length issues
        prefix = "7z_" if os.name == 'nt' else "7z_unified_"
        with tempfile.TemporaryDirectory(prefix=prefix) as temp_dir:
            try:
                files_copied = self._copy_files_to_temp(files, temp_dir, base_dir)
                
                if files_copied == 0:
                    return False, "No files could be copied for compression"
                    
                log(f"Copied {files_copied} files to temp directory, compressing...", log_type='INFO')
                
                # Create a proper folder structure inside the archive
                # Extract the mod name from the archive path to use as the folder name
                archive_name = Path(archive_path).stem  # Get name without .7z extension
                
                # Create a subdirectory with the proper mod name
                mod_folder = os.path.join(temp_dir, archive_name)
                os.makedirs(mod_folder, exist_ok=True)
                
                # Move all files from temp_dir to mod_folder
                for item in os.listdir(temp_dir):
                    if item != archive_name:  # Don't move the folder we just created
                        src = os.path.join(temp_dir, item)
                        dst = os.path.join(mod_folder, item)
                        if os.path.isdir(src):
                            shutil.move(src, dst)
                        else:
                            shutil.move(src, dst)
                
                # Now compress the mod_folder (which contains the proper mod name folder)
                return self._compress_directory_direct(mod_folder, archive_path)
                
            except Exception as e:
                return False, f"File preparation failed: {e}"
                
    def _copy_files_to_temp(self, files: List[str], temp_dir: str, base_dir: Optional[str] = None) -> int:
        """Copy files to temporary directory for compression."""
        files_copied = 0
        
        for file_path in files:
            if not os.path.exists(file_path):
                log(f"File not found: {file_path}", log_type='WARNING')
                continue
                
            try:
                if base_dir and os.path.commonpath([os.path.abspath(file_path), os.path.abspath(base_dir)]) == os.path.abspath(base_dir):
                    # Maintain relative structure if file is under base_dir
                    rel_path = os.path.relpath(file_path, base_dir)
                    dest_path = os.path.join(temp_dir, rel_path)
                else:
                    # For loose files, use filename only
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(temp_dir, filename)
                    
                    # Handle filename conflicts
                    counter = 1
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(filename)
                        dest_path = os.path.join(temp_dir, f"{name}_{counter}{ext}")
                        counter += 1
                
                # Create destination directory and copy file
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
                files_copied += 1
                
            except Exception as e:
                log(f"Failed to copy {file_path}: {e}", log_type='WARNING')
                
        return files_copied
        
    def extract_archive(self, archive_path: str, extract_dir: str) -> Tuple[bool, str]:
        """
        Extract 7z archive to directory.
        
        Args:
            archive_path: Archive to extract
            extract_dir: Directory to extract to
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_available():
            return False, "7z command not available"
            
        if not os.path.exists(archive_path):
            return False, f"Archive not found: {archive_path}"
            
        try:
            os.makedirs(extract_dir, exist_ok=True)
            
            cmd = [
                self.sevenz_cmd, 'x',
                os.path.abspath(archive_path),
                f'-o{os.path.abspath(extract_dir)}',
                '-y'  # Yes to all prompts
            ]
            
            log(f"7z extract: {' '.join(cmd)}", log_type='DEBUG')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return True, f"Archive extracted successfully to: {extract_dir}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                return False, f"7z extraction failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "7z extraction timed out (>5 minutes)"
        except Exception as e:
            return False, f"7z extraction error: {e}"
            
    def get_archive_info(self, archive_path: str) -> Tuple[bool, str, int]:
        """
        Get information about an archive.
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            Tuple of (success: bool, message: str, file_count: int)
        """
        if not self.is_available():
            return False, "7z command not available", 0
            
        if not os.path.exists(archive_path):
            return False, f"Archive not found: {archive_path}", 0
            
        try:
            # Use 7z to list archive contents and count files
            cmd = [self.sevenz_cmd, 'l', archive_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Count files in the output (look for lines that start with file info)
                lines = result.stdout.split('\n')
                file_count = 0
                for line in lines:
                    # Look for lines that contain file information (not headers)
                    if line.strip() and not line.startswith('--') and not line.startswith('Archive:') and not line.startswith('Path ='):
                        # Check if it looks like a file entry (has size info)
                        if any(char.isdigit() for char in line) and (' ' in line):
                            file_count += 1
                
                return True, f"Archive info retrieved: {file_count} files", file_count
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown 7z error"
                return False, f"7z info failed: {error_msg}", 0
                
        except subprocess.TimeoutExpired:
            return False, "7z info timed out", 0
        except Exception as e:
            return False, f"7z info error: {e}", 0


# Global compression service instance
_compression_service = None


def get_compression_service(compression_level: int = 3) -> CompressionService:
    """Get global compression service instance."""
    global _compression_service
    if _compression_service is None or _compression_service.compression_level != compression_level:
        _compression_service = CompressionService(compression_level)
    return _compression_service


def compress_directory(source_dir: str, archive_path: str, compression_level: int = 3) -> Tuple[bool, str]:
    """Convenience function to compress directory."""
    service = get_compression_service(compression_level)
    return service.compress_directory(source_dir, archive_path)


def compress_files(files: List[str], archive_path: str, base_dir: Optional[str] = None, compression_level: int = 3) -> Tuple[bool, str]:
    """Convenience function to compress files."""
    service = get_compression_service(compression_level)
    return service.compress_files(files, archive_path, base_dir)


def extract_archive(archive_path: str, extract_dir: str) -> Tuple[bool, str]:
    """Convenience function to extract archive."""
    service = get_compression_service()
    return service.extract_archive(archive_path, extract_dir)


def is_7z_available() -> bool:
    """Check if 7z CLI is available."""
    service = get_compression_service()
    return service.is_available()


class Compressor:
    """
    Compressor class - maintains backward compatibility with existing code.
    
    This is a simple wrapper around CompressionService to maintain the same interface
    that existing code expects from the Compressor class.
    """
    
    def __init__(self, compression_level: int = 3):
        """
        Initialize compressor.
        
        Args:
            compression_level: 7z compression level (0-9)
        """
        self.compression_level = compression_level
        self.service = get_compression_service(compression_level)
        
    def compress_files(self, files: List[str], archive_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Compress list of files into 7z archive.
        
        Args:
            files: List of file paths to compress
            archive_path: Output path for 7z archive
            base_dir: Base directory for relative paths (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.service.compress_files(files, archive_path, base_dir)
        
    def compress_bulk_directory(self, source_dir: str, archive_path: str) -> Tuple[bool, str]:
        """
        Compress entire directory using 7z CLI.
        
        Args:
            source_dir: Directory to compress
            archive_path: Output path for 7z archive
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.service.compress_directory(source_dir, archive_path)
        
    def compress_directory_with_folder_name(self, source_dir: str, archive_path: str, folder_name: str) -> Tuple[bool, str]:
        """
        Compress directory contents with a custom folder name inside the archive.
        
        Args:
            source_dir: Directory to compress
            archive_path: Output archive path
            folder_name: Name of the folder inside the archive
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.service.compress_directory_with_folder_name(source_dir, archive_path, folder_name)
        
    def get_archive_info(self, archive_path: str) -> Tuple[bool, str, int]:
        """
        Get information about an archive.
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            Tuple of (success: bool, message: str, file_count: int)
        """
        return self.service.get_archive_info(archive_path)
