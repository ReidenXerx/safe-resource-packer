"""
Universal BSArch Service

Provides a unified service for BSArch detection, validation, and execution.
Handles all BSArch operations with proper error handling and logging.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from .bsarch_detector import get_bsarch_detector, detect_bsarch_global
from .dynamic_progress import log
from .utils import format_bytes


class BSArchService:
    """Universal service for BSArch operations."""
    
    def __init__(self, game_type: str = "skyrim"):
        """
        Initialize BSArch service.
        
        Args:
            game_type: Target game type ("skyrim" or "fallout4")
        """
        self.game_type = game_type.lower()
        self.detector = get_bsarch_detector()
        self._bsarch_path = None
        self._bsarch_validated = False
    
    def _get_bsarch_path(self, interactive: bool = False) -> Optional[str]:
        """
        Get validated BSArch path.
        
        Args:
            interactive: Whether to ask user if BSArch not found
            
        Returns:
            Path to BSArch executable or None if not available
        """
        if self._bsarch_validated and self._bsarch_path:
            return self._bsarch_path
        
        # Try to get cached path first
        cached_path = self.detector.get_bsarch_path()
        if cached_path:
            if self._validate_bsarch_path(cached_path):
                self._bsarch_path = cached_path
                self._bsarch_validated = True
                log(f"✅ Using cached BSArch: {cached_path}", log_type='DEBUG')
                return cached_path
            else:
                log(f"⚠️ Cached BSArch path is invalid: {cached_path}", log_type='WARNING')
                self.detector.clear_bsarch_cache()
        
        # Try global detection
        success, message = detect_bsarch_global(interactive=interactive)
        if success:
            # Extract path from message
            if ":" in message:
                detected_path = message.split(":", 1)[1].strip()
                if self._validate_bsarch_path(detected_path):
                    self._bsarch_path = detected_path
                    self._bsarch_validated = True
                    log(f"✅ Using detected BSArch: {detected_path}", log_type='DEBUG')
                    return detected_path
        
        log(f"❌ BSArch not available: {message}", log_type='ERROR')
        return None
    
    def _validate_bsarch_path(self, path: str) -> bool:
        """
        Validate BSArch executable path.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            if not os.path.exists(path):
                log(f"❌ BSArch path does not exist: {path}", log_type='DEBUG')
                return False
            
            if not os.access(path, os.X_OK):
                log(f"❌ BSArch path is not executable: {path}", log_type='DEBUG')
                return False
            
            file_size = os.path.getsize(path)
            if file_size < 1000:
                log(f"❌ BSArch file too small ({file_size} bytes): {path}", log_type='DEBUG')
                return False
            
            # Try to run BSArch with --help to verify it's actually BSArch
            try:
                result = subprocess.run([path, "--help"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and "BSArch" in result.stdout:
                    log(f"✅ BSArch validation successful: {path}", log_type='DEBUG')
                    return True
                else:
                    log(f"❌ BSArch validation failed - not a valid BSArch executable: {path}", log_type='DEBUG')
                    return False
            except subprocess.TimeoutExpired:
                log(f"❌ BSArch validation timeout: {path}", log_type='DEBUG')
                return False
            except Exception as e:
                log(f"❌ BSArch validation error: {e}", log_type='DEBUG')
                return False
                
        except Exception as e:
            log(f"❌ BSArch path validation error: {e}", log_type='DEBUG')
            return False
    
    def is_available(self, interactive: bool = False, force_refresh: bool = False) -> Tuple[bool, str]:
        """
        Check if BSArch is available and working.
        
        Args:
            interactive: Whether to ask user if BSArch not found
            force_refresh: Whether to force refresh and clear cache
            
        Returns:
            Tuple of (is_available, message)
        """
        if force_refresh:
            log("🔄 Force refreshing BSArch detection...", log_type='INFO')
            self._bsarch_path = None
            self._bsarch_validated = False
            self.detector.clear_bsarch_cache()
        
        bsarch_path = self._get_bsarch_path(interactive=interactive)
        if bsarch_path:
            return True, f"BSArch available at: {bsarch_path}"
        else:
            return False, "BSArch not available"
    
    def execute_bsarch(self, 
                      source_dir: str, 
                      output_path: str, 
                      files: List[str],
                      interactive: bool = False) -> Tuple[bool, str]:
        """
        Execute BSArch to create archive.
        
        Args:
            source_dir: Directory containing files to pack
            output_path: Path for output archive
            files: List of files to include in archive
            interactive: Whether to ask user if BSArch not found
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Get validated BSArch path
            bsarch_path = self._get_bsarch_path(interactive=interactive)
            if not bsarch_path:
                return False, "BSArch not available"
            
            # Additional validation before execution
            if not os.path.exists(bsarch_path):
                log(f"❌ BSArch path does not exist: {bsarch_path}", log_type='ERROR')
                return False, f"BSArch path does not exist: {bsarch_path}"
            
            if not os.access(bsarch_path, os.X_OK):
                log(f"❌ BSArch path is not executable: {bsarch_path}", log_type='ERROR')
                return False, f"BSArch path is not executable: {bsarch_path}"
            
            # Test BSArch with a simple command to verify it works
            log(f"🔧 Testing BSArch with --help command...", log_type='DEBUG')
            try:
                test_result = subprocess.run([bsarch_path, "--help"], 
                                           capture_output=True, text=True, timeout=10,
                                           cwd=os.path.dirname(bsarch_path) if os.path.dirname(bsarch_path) else None)
                if test_result.returncode != 0:
                    log(f"⚠️ BSArch --help test failed: {test_result.stderr}", log_type='WARNING')
                else:
                    log(f"✅ BSArch --help test successful", log_type='DEBUG')
            except Exception as e:
                log(f"⚠️ BSArch --help test error: {e}", log_type='WARNING')
            
            # Validate inputs
            if not os.path.exists(source_dir):
                return False, f"Source directory does not exist: {source_dir}"
            
            if not files:
                return False, "No files to pack"
            
            # Create temporary staging directory
            with tempfile.TemporaryDirectory(prefix="bsarch_staging_") as temp_dir:
                # Stage files maintaining directory structure
                self._stage_files(files, temp_dir, source_dir)
                
                # Build BSArch command
                cmd = self._build_bsarch_command(bsarch_path, temp_dir, output_path)
                
                # Log command for debugging
                log(f"🔧 Executing BSArch: {' '.join(cmd)}", log_type='INFO')
                log(f"📦 Creating {self.game_type.upper()} archive with {len(files)} files", log_type='INFO')
                log(f"🔧 BSArch path: {bsarch_path}", log_type='DEBUG')
                log(f"🔧 Source dir: {temp_dir}", log_type='DEBUG')
                log(f"🔧 Output path: {output_path}", log_type='DEBUG')
                log(f"🔧 Working directory: {os.getcwd()}", log_type='DEBUG')
                
                # Execute BSArch with better error handling
                timeout = 300 + (len(files) // 100) * 60  # Base 5min + 1min per 100 files
                try:
                    # Set working directory to BSArch's directory (Windows requirement)
                    bsarch_dir = os.path.dirname(bsarch_path)
                    if not bsarch_dir:
                        bsarch_dir = os.getcwd()
                    
                    log(f"🔧 Running BSArch from directory: {bsarch_dir}", log_type='DEBUG')
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, 
                                          cwd=bsarch_dir, shell=False)
                except FileNotFoundError as e:
                    log(f"❌ BSArch executable not found: {e}", log_type='ERROR')
                    log(f"❌ Command was: {' '.join(cmd)}", log_type='ERROR')
                    log(f"❌ Working directory was: {bsarch_dir}", log_type='ERROR')
                    return False, f"BSArch executable not found: {e}"
                except Exception as e:
                    log(f"❌ BSArch execution error: {e}", log_type='ERROR')
                    log(f"❌ Command was: {' '.join(cmd)}", log_type='ERROR')
                    log(f"❌ Working directory was: {bsarch_dir}", log_type='ERROR')
                    return False, f"BSArch execution error: {e}"
                
                if result.returncode == 0:
                    # Verify archive was created
                    if os.path.exists(output_path):
                        archive_size = os.path.getsize(output_path)
                        log(f"✅ Archive created successfully: {output_path} ({format_bytes(archive_size)})", log_type='SUCCESS')
                        return True, f"Archive created successfully ({format_bytes(archive_size)})"
                    else:
                        return False, "BSArch completed but archive file not found"
                else:
                    error_msg = result.stderr or "Unknown BSArch error"
                    stdout_msg = result.stdout or "No stdout"
                    log(f"❌ BSArch stderr: {error_msg}", log_type='ERROR')
                    log(f"❌ BSArch stdout: {stdout_msg}", log_type='ERROR')
                    return False, f"BSArch execution failed: {error_msg}"
                    
        except subprocess.TimeoutExpired:
            return False, f"BSArch timed out after {timeout // 60} minutes"
        except Exception as e:
            log(f"❌ BSArch execution error: {e}", log_type='ERROR')
            return False, f"BSArch execution error: {e}"
    
    def _stage_files(self, files: List[str], temp_dir: str, source_dir: str) -> None:
        """
        Stage files in temporary directory maintaining structure.
        
        Args:
            files: List of files to stage
            temp_dir: Temporary directory for staging
            source_dir: Source directory (for relative paths)
        """
        for file_path in files:
            if not os.path.exists(file_path):
                log(f"⚠️ File not found, skipping: {file_path}", log_type='WARNING')
                continue
            
            # Calculate relative path from source directory
            try:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(temp_dir, rel_path)
                
                # Create destination directory
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, dest_path)
                
            except Exception as e:
                log(f"⚠️ Failed to stage file {file_path}: {e}", log_type='WARNING')
    
    def _build_bsarch_command(self, bsarch_path: str, source_dir: str, output_path: str) -> List[str]:
        """
        Build BSArch command with appropriate arguments.
        
        Args:
            bsarch_path: Path to BSArch executable
            source_dir: Directory containing files to pack
            output_path: Path for output archive
            
        Returns:
            List of command arguments
        """
        # Ensure paths are properly formatted for Windows
        bsarch_path = os.path.normpath(bsarch_path)
        source_dir = os.path.normpath(source_dir)
        output_path = os.path.normpath(output_path)
        
        cmd = [
            bsarch_path,
            "pack",
            source_dir,
            output_path,
            "-mt",  # Multi-threaded
            "-c",   # Compression enabled
            "-f"    # Force overwrite
        ]
        
        if self.game_type == "fallout4":
            cmd.extend(["-fo4", "-dds"])  # Fallout 4 format with DDS compression
        else:
            cmd.extend(["-sse", "-dds"])  # Skyrim Special Edition format with DDS compression
        
        return cmd
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get BSArch service status.
        
        Returns:
            Dictionary with service status information
        """
        return {
            'bsarch_path': self._bsarch_path,
            'bsarch_validated': self._bsarch_validated,
            'game_type': self.game_type,
            'is_available': self._bsarch_path is not None
        }


# Global service instances
_bsarch_services = {}

def get_bsarch_service(game_type: str = "skyrim") -> BSArchService:
    """
    Get global BSArch service instance for specific game type.
    
    Args:
        game_type: Target game type
        
    Returns:
        BSArchService instance
    """
    global _bsarch_services
    game_key = game_type.lower()
    
    if game_key not in _bsarch_services:
        _bsarch_services[game_key] = BSArchService(game_type=game_key)
    
    return _bsarch_services[game_key]


def execute_bsarch_universal(source_dir: str, 
                            output_path: str, 
                            files: List[str],
                            game_type: str = "skyrim",
                            interactive: bool = False) -> Tuple[bool, str]:
    """
    Universal function to execute BSArch.
    
    Args:
        source_dir: Directory containing files to pack
        output_path: Path for output archive
        files: List of files to include in archive
        game_type: Target game type
        interactive: Whether to ask user if BSArch not found
        
    Returns:
        Tuple of (success, message)
    """
    service = get_bsarch_service(game_type)
    return service.execute_bsarch(source_dir, output_path, files, interactive=interactive)


def check_bsarch_availability_universal(game_type: str = "skyrim", 
                                        interactive: bool = False,
                                        force_refresh: bool = False) -> Tuple[bool, str]:
    """
    Universal function to check BSArch availability.
    
    Args:
        game_type: Target game type
        interactive: Whether to ask user if BSArch not found
        force_refresh: Whether to force refresh and clear cache
        
    Returns:
        Tuple of (is_available, message)
    """
    service = get_bsarch_service(game_type)
    return service.is_available(interactive=interactive, force_refresh=force_refresh)
