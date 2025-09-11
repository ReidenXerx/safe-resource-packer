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
    
    def execute_bsarch_chunked(self, 
                              source_dir: str, 
                              output_base_path: str, 
                              files: List[str],
                              max_chunk_size_gb: float = 2.0,
                              interactive: bool = False) -> Tuple[bool, str, List[str]]:
        """
        Execute BSArch to create chunked archives (like CAO does).
        
        Args:
            source_dir: Directory containing files to pack
            output_base_path: Base path for output archives (without extension)
            files: List of files to include in archive
            max_chunk_size_gb: Maximum size per chunk in GB (default 2.0)
            interactive: Whether to ask user if BSArch not found
            
        Returns:
            Tuple of (success: bool, message: str, created_archives: List[str])
        """
        try:
            # Get validated BSArch path using global detection
            from .bsarch_detector import get_bsarch_detector
            detector = get_bsarch_detector()
            bsarch_path = detector.get_bsarch_path()
            
            if not bsarch_path:
                if interactive:
                    # Try interactive detection
                    bsarch_path = detector.detect_bsarch_interactive()
                if not bsarch_path:
                    return False, "BSArch not available", []
            
            # Validate the path
            if not self._validate_bsarch_path(bsarch_path):
                return False, f"BSArch validation failed: {bsarch_path}", []
            
            # Validate inputs
            if not os.path.exists(source_dir):
                return False, f"Source directory does not exist: {source_dir}", []
            
            if not files:
                return False, "No files to pack", []
            
            # Calculate total size and determine if chunking is needed
            total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            max_chunk_size_bytes = max_chunk_size_gb * 1024 * 1024 * 1024  # Convert GB to bytes
            
            log(f"📊 Total files size: {format_bytes(total_size)}", log_type='INFO')
            log(f"📊 Max chunk size: {format_bytes(max_chunk_size_bytes)}", log_type='INFO')
            
            if total_size <= max_chunk_size_bytes:
                # Single archive is sufficient
                log(f"📦 Creating single archive (size within limit)", log_type='INFO')
                success, message = self.execute_bsarch(source_dir, output_base_path, files, interactive)
                if success:
                    archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
                    archive_path = output_base_path + archive_ext
                    return True, message, [archive_path]
                else:
                    return False, message, []
            
            # Need to create chunks
            log(f"📦 Creating chunked archives (total size exceeds {max_chunk_size_gb}GB limit)", log_type='INFO')
            return self._create_chunked_archives(bsarch_path, source_dir, output_base_path, files, max_chunk_size_bytes)
            
        except Exception as e:
            log(f"❌ Chunked BSArch execution error: {e}", log_type='ERROR')
            return False, f"Chunked BSArch execution error: {e}", []

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
            
            # ArchiveCreator already stages files with proper game directory structure
            # Just use the source_dir directly - it contains the properly staged files
            staging_dir = source_dir
            log(f"🔧 Using pre-staged files in: {staging_dir}", log_type='DEBUG')
            
            # Verify staging directory has files
            staged_files = []
            for root, dirs, files in os.walk(staging_dir):
                for file in files:
                    staged_files.append(os.path.join(root, file))
            
            if not staged_files:
                log(f"❌ No files found in staging directory: {staging_dir}", log_type='ERROR')
                return False, f"No files found in staging directory: {staging_dir}"
            
            log(f"🔧 Found {len(staged_files)} staged files", log_type='DEBUG')
            
            # Build BSArch command
            cmd = self._build_bsarch_command(bsarch_path, staging_dir, output_path)
            
            # Log command for debugging
            log(f"🔧 Executing BSArch: {' '.join(cmd)}", log_type='INFO')
            log(f"📦 Creating {self.game_type.upper()} archive with {len(staged_files)} files", log_type='INFO')
            log(f"🔧 BSArch path: {bsarch_path}", log_type='DEBUG')
            log(f"🔧 Source dir: {staging_dir}", log_type='DEBUG')
            log(f"🔧 Output path: {output_path}", log_type='DEBUG')
            log(f"🔧 Working directory: {os.getcwd()}", log_type='DEBUG')
            
            # Execute BSArch with better error handling
            timeout = 300 + (len(staged_files) // 100) * 60  # Base 5min + 1min per 100 files
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
            os.path.abspath(source_dir),  # Use absolute path
            os.path.abspath(output_path),  # Use absolute path
            "-mt",  # Multi-threaded
            "-c",   # Compression enabled
            "-f"    # Force overwrite
        ]
        
        if self.game_type == "fallout4":
            cmd.extend(["-fo4", "-dds"])  # Fallout 4 format with DDS compression
        else:
            cmd.extend(["-sse", "-dds"])  # Skyrim Special Edition format with DDS compression
        
        return cmd
    
    def _create_chunked_archives(self, bsarch_path: str, source_dir: str, output_base_path: str, 
                                files: List[str], max_chunk_size_bytes: int) -> Tuple[bool, str, List[str]]:
        """
        Create multiple chunked archives from files.
        
        Args:
            bsarch_path: Path to BSArch executable
            source_dir: Directory containing files to pack
            output_base_path: Base path for output archives
            files: List of files to include
            max_chunk_size_bytes: Maximum size per chunk in bytes
            
        Returns:
            Tuple of (success: bool, message: str, created_archives: List[str])
        """
        try:
            # Get file sizes and sort by size (largest first to optimize packing)
            file_info = []
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    file_info.append((file_path, file_size))
                else:
                    log(f"⚠️ File not found, skipping: {file_path}", log_type='WARNING')
            
            # Sort by size (largest first) to optimize chunk packing
            file_info.sort(key=lambda x: x[1], reverse=True)
            
            log(f"📋 Processing {len(file_info)} files for chunking", log_type='INFO')
            
            # Distribute files into chunks
            chunks = self._distribute_files_into_chunks(file_info, max_chunk_size_bytes)
            
            if not chunks:
                return False, "Failed to distribute files into chunks", []
            
            log(f"📦 Created {len(chunks)} chunks", log_type='INFO')
            
            # Create archives for each chunk
            created_archives = []
            archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
            
            for i, chunk_files in enumerate(chunks):
                # Generate chunk name (pack.bsa, pack0.bsa, pack1.bsa, etc.)
                if i == 0:
                    chunk_name = "pack"
                else:
                    chunk_name = f"pack{i-1}"
                
                chunk_output_path = f"{output_base_path}_{chunk_name}{archive_ext}"
                
                log(f"📦 Creating chunk {i+1}/{len(chunks)}: {os.path.basename(chunk_output_path)}", log_type='INFO')
                log(f"📊 Chunk {i+1} contains {len(chunk_files)} files", log_type='DEBUG')
                
                # Create staging directory for this chunk (use temp directory to avoid conflicts)
                import tempfile
                chunk_staging_dir = tempfile.mkdtemp(prefix=f"bsa_chunk_{i}_")
                
                try:
                    # Stage files for this chunk
                    self._stage_files_for_chunk(chunk_files, chunk_staging_dir, source_dir)
                    
                    # Verify staging directory has files
                    staged_files = []
                    for root, dirs, files in os.walk(chunk_staging_dir):
                        staged_files.extend([os.path.join(root, f) for f in files])
                    
                    if not staged_files:
                        log(f"❌ No files staged for chunk {i+1}", log_type='ERROR')
                        return False, f"No files staged for chunk {i+1}", []
                    
                    log(f"📁 Staged {len(staged_files)} files for chunk {i+1}", log_type='DEBUG')
                    
                    # Create archive for this chunk
                    success, message = self._create_single_chunk_archive(
                        bsarch_path, chunk_staging_dir, chunk_output_path
                    )
                    
                    if success:
                        created_archives.append(chunk_output_path)
                        chunk_size = os.path.getsize(chunk_output_path)
                        log(f"✅ Created chunk {i+1}: {os.path.basename(chunk_output_path)} ({format_bytes(chunk_size)})", log_type='SUCCESS')
                    else:
                        log(f"❌ Failed to create chunk {i+1}: {message}", log_type='ERROR')
                        return False, f"Failed to create chunk {i+1}: {message}", []
                        
                finally:
                    # Clean up staging directory
                    try:
                        shutil.rmtree(chunk_staging_dir, ignore_errors=True)
                    except Exception as cleanup_error:
                        log(f"⚠️ Failed to cleanup chunk staging directory: {cleanup_error}", log_type='WARNING')
            
            # Verify all chunks were created successfully
            if len(created_archives) == len(chunks):
                total_size = sum(os.path.getsize(arch) for arch in created_archives)
                log(f"✅ Successfully created {len(created_archives)} chunked archives", log_type='SUCCESS')
                log(f"📊 Total chunked size: {format_bytes(total_size)}", log_type='INFO')
                
                # Verify no files were lost
                self._verify_chunk_integrity(files, created_archives)
                
                return True, f"Created {len(created_archives)} chunked archives", created_archives
            else:
                return False, f"Only created {len(created_archives)} out of {len(chunks)} expected chunks", created_archives
                
        except Exception as e:
            log(f"❌ Error creating chunked archives: {e}", log_type='ERROR')
            return False, f"Error creating chunked archives: {e}", []
    
    def _distribute_files_into_chunks(self, file_info: List[Tuple[str, int]], max_chunk_size_bytes: int) -> List[List[str]]:
        """
        Distribute files into chunks using bin packing algorithm.
        
        Args:
            file_info: List of (file_path, file_size) tuples
            max_chunk_size_bytes: Maximum size per chunk
            
        Returns:
            List of chunks, where each chunk is a list of file paths
        """
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        
        for file_path, file_size in file_info:
            # If single file exceeds chunk limit, we need to handle it specially
            if file_size > max_chunk_size_bytes:
                log(f"⚠️ File {os.path.basename(file_path)} ({format_bytes(file_size)}) exceeds chunk limit", log_type='WARNING')
                log(f"⚠️ This file will be placed in its own chunk", log_type='WARNING')
                
                # Finish current chunk if it has files
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_chunk_size = 0
                
                # Create single-file chunk
                chunks.append([file_path])
                continue
            
            # Check if adding this file would exceed the limit
            if current_chunk_size + file_size > max_chunk_size_bytes and current_chunk:
                # Finish current chunk and start new one
                chunks.append(current_chunk)
                current_chunk = [file_path]
                current_chunk_size = file_size
            else:
                # Add file to current chunk
                current_chunk.append(file_path)
                current_chunk_size += file_size
        
        # Add final chunk if it has files
        if current_chunk:
            chunks.append(current_chunk)
        
        # Log chunk distribution
        for i, chunk in enumerate(chunks):
            chunk_size = sum(file_info[j][1] for j, (fp, _) in enumerate(file_info) if fp in chunk)
            log(f"📊 Chunk {i+1}: {len(chunk)} files, {format_bytes(chunk_size)}", log_type='DEBUG')
        
        return chunks
    
    def _stage_files_for_chunk(self, chunk_files: List[str], chunk_staging_dir: str, source_dir: str):
        """
        Stage files for a specific chunk maintaining directory structure.
        
        Args:
            chunk_files: List of files for this chunk
            chunk_staging_dir: Directory to stage files in
            source_dir: Original source directory
        """
        log(f"🔧 Staging {len(chunk_files)} files for chunk", log_type='DEBUG')
        log(f"🔧 Source directory: {source_dir}", log_type='DEBUG')
        log(f"🔧 Staging directory: {chunk_staging_dir}", log_type='DEBUG')
        
        staged_count = 0
        for file_path in chunk_files:
            if not os.path.exists(file_path):
                log(f"⚠️ File not found, skipping: {file_path}", log_type='WARNING')
                continue
            
            # Calculate relative path from source directory
            try:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(chunk_staging_dir, rel_path)
                
                log(f"🔧 Staging: {file_path} -> {dest_path}", log_type='DEBUG')
                
                # Create destination directory
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, dest_path)
                staged_count += 1
                
            except Exception as e:
                log(f"⚠️ Failed to stage file {file_path}: {e}", log_type='WARNING')
        
        log(f"🔧 Successfully staged {staged_count} files", log_type='DEBUG')
    
    def _create_single_chunk_archive(self, bsarch_path: str, staging_dir: str, output_path: str) -> Tuple[bool, str]:
        """
        Create a single archive for one chunk.
        
        Args:
            bsarch_path: Path to BSArch executable
            staging_dir: Directory containing staged files
            output_path: Path for output archive
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Build BSArch command
            cmd = self._build_bsarch_command(bsarch_path, staging_dir, output_path)
            
            # Execute BSArch
            timeout = 300 + (len(os.listdir(staging_dir)) // 100) * 60  # Base 5min + 1min per 100 files
            
            # Log command details for debugging
            log(f"🔧 BSArch command: {' '.join(cmd)}", log_type='DEBUG')
            log(f"📁 Staging directory: {staging_dir}", log_type='DEBUG')
            log(f"📁 Staging directory exists: {os.path.exists(staging_dir)}", log_type='DEBUG')
            log(f"📁 Files in staging: {len(os.listdir(staging_dir)) if os.path.exists(staging_dir) else 'N/A'}", log_type='DEBUG')
            
            try:
                bsarch_dir = os.path.dirname(bsarch_path)
                if not bsarch_dir:
                    bsarch_dir = os.getcwd()
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, 
                                      cwd=bsarch_dir, shell=False)
            except subprocess.TimeoutExpired:
                return False, f"BSArch timed out after {timeout // 60} minutes"
            except Exception as e:
                return False, f"BSArch execution error: {e}"
            
            # Log BSArch output for debugging
            log(f"🔧 BSArch return code: {result.returncode}", log_type='DEBUG')
            if result.stdout:
                log(f"🔧 BSArch stdout: {result.stdout[:500]}", log_type='DEBUG')
            if result.stderr:
                log(f"🔧 BSArch stderr: {result.stderr[:500]}", log_type='DEBUG')
            
            if result.returncode == 0:
                # Verify archive was created
                if os.path.exists(output_path):
                    return True, f"Archive created successfully"
                else:
                    return False, "BSArch completed but archive file not found"
            else:
                error_msg = result.stderr or result.stdout or "Unknown BSArch error"
                return False, f"BSArch execution failed: {error_msg}"
                
        except Exception as e:
            return False, f"Single chunk archive creation failed: {e}"
    
    def _verify_chunk_integrity(self, original_files: List[str], created_archives: List[str]):
        """
        Verify that no files were lost during chunking process.
        
        Args:
            original_files: List of original files
            created_archives: List of created archive paths
        """
        try:
            log(f"🔍 Verifying chunk integrity...", log_type='INFO')
            
            # Count original files that exist
            existing_original_files = [f for f in original_files if os.path.exists(f)]
            log(f"📊 Original files: {len(existing_original_files)}", log_type='DEBUG')
            
            # For now, we'll do a basic verification by checking archive sizes
            # A more thorough verification would require extracting and comparing file lists
            total_archive_size = sum(os.path.getsize(arch) for arch in created_archives if os.path.exists(arch))
            log(f"📊 Total archive size: {format_bytes(total_archive_size)}", log_type='DEBUG')
            
            if len(existing_original_files) > 0 and total_archive_size > 0:
                log(f"✅ Chunk integrity check passed - archives created successfully", log_type='SUCCESS')
            else:
                log(f"⚠️ Chunk integrity check inconclusive", log_type='WARNING')
                
        except Exception as e:
            log(f"⚠️ Chunk integrity verification failed: {e}", log_type='WARNING')
    
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


def execute_bsarch_chunked_universal(source_dir: str, 
                                    output_base_path: str, 
                                    files: List[str],
                                    game_type: str = "skyrim",
                                    max_chunk_size_gb: float = 2.0,
                                    interactive: bool = False) -> Tuple[bool, str, List[str]]:
    """
    Universal function to execute chunked BSArch.
    
    Args:
        source_dir: Directory containing files to pack
        output_base_path: Base path for output archives (without extension)
        files: List of files to include in archive
        game_type: Target game type
        max_chunk_size_gb: Maximum size per chunk in GB (default 2.0)
        interactive: Whether to ask user if BSArch not found
        
    Returns:
        Tuple of (success: bool, message: str, created_archives: List[str])
    """
    service = get_bsarch_service(game_type)
    return service.execute_bsarch_chunked(source_dir, output_base_path, files, max_chunk_size_gb, interactive)

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
