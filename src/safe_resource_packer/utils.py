"""
Utility functions for Safe Resource Packer.
"""

import os
import sys
import hashlib
import threading
import platform
import shutil
import unicodedata
from datetime import datetime


# Check if rich is available for colored output
try:
    from rich.console import Console
    RICH_CONSOLE = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_CONSOLE = None
    RICH_AVAILABLE = False


def file_hash(path, chunk_size=8192):
    """
    Calculate SHA1 hash of a file using streaming for memory efficiency.

    Args:
        path (str): Path to file
        chunk_size (int): Size of chunks to read (default 8KB)

    Returns:
        str or None: SHA1 hash or None if error
    """
    try:
        # Check file size first to detect potential issues
        file_size = os.path.getsize(path)
        if file_size > 8 * 1024 * 1024 * 1024:  # 8GB limit (much more generous)
            print(f"[HASH WARNING] Very large file detected: {path} ({file_size / (1024**3):.1f}GB)")
        
        hash_obj = hashlib.sha1()
        with open(path, 'rb') as f:
            # Stream file in chunks to avoid memory issues
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except OSError as e:
        print(f"[HASH FAIL] {path}: OS Error - {e}")
        return None
    except MemoryError as e:
        print(f"[HASH FAIL] {path}: Memory exhausted - {e}")
        return None
    except Exception as e:
        print(f"[HASH FAIL] {path}: {e}")
        return None


def validate_path_length(path, max_length=None):
    """
    Validate path length for cross-platform compatibility.
    
    Args:
        path (str): Path to validate
        max_length (int): Maximum allowed length (defaults based on OS)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if max_length is None:
        # Much more generous limits - modern Windows supports long paths
        # Only enforce truly problematic lengths
        max_length = 32767 if platform.system() == 'Windows' else 4096
    
    if len(path) > max_length:
        return False, f"Path too long: {len(path)} chars (max {max_length})"
    
    # Skip character validation - let the OS handle invalid paths naturally
    # This avoids false positives with valid Windows paths like C:\Users\...
    
    # Also skip reserved name checking - modern Windows handles this gracefully
    # and it can cause false positives with legitimate mod files
    
    return True, ""


def sanitize_filename(filename):
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Normalize Unicode characters
    filename = unicodedata.normalize('NFKC', filename)
    
    # Replace invalid characters
    if platform.system() == 'Windows':
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
    
    # Ensure it's not empty
    if not filename.strip():
        filename = "unnamed_file"
    
    return filename


def check_disk_space(path, required_bytes, safety_margin=0.1):
    """
    Check if there's enough disk space at the given path.
    
    Args:
        path (str): Path to check
        required_bytes (int): Required space in bytes
        safety_margin (float): Safety margin as fraction (default 10%)
        
    Returns:
        tuple: (has_space, available_bytes, required_with_margin)
    """
    try:
        # Get disk usage statistics
        total, used, free = shutil.disk_usage(path)
        
        # Calculate required space with safety margin
        required_with_margin = int(required_bytes * (1 + safety_margin))
        
        has_space = free >= required_with_margin
        
        return has_space, free, required_with_margin
        
    except Exception as e:
        print(f"Failed to check disk space for {path}: {e}")
        # Assume we have space if we can't check
        return True, 0, required_bytes


def format_bytes(bytes_value):
    """
    Format bytes in human-readable format.
    
    Args:
        bytes_value (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024**2:
        return f"{bytes_value/1024:.1f} KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value/(1024**2):.1f} MB"
    else:
        return f"{bytes_value/(1024**3):.1f} GB"


def safe_walk(path, followlinks=False, max_depth=20):
    """
    Safe directory walking with symlink and depth protection.
    
    Args:
        path (str): Directory to walk
        followlinks (bool): Whether to follow symbolic links
        max_depth (int): Maximum recursion depth
        
    Yields:
        tuple: (root, dirs, files) like os.walk()
    """
    visited = set()
    
    def _walk_recursive(current_path, current_depth):
        if current_depth > max_depth:
            print(f"Max depth {max_depth} reached, stopping walk at: {current_path}")
            return
            
        try:
            # Resolve path to detect circular references
            real_path = os.path.realpath(current_path)
            if real_path in visited:
                print(f"Circular reference detected, skipping: {current_path}")
                return
            visited.add(real_path)
            
            # Check if path is accessible
            if not os.path.exists(current_path) or not os.path.isdir(current_path):
                return
                
            # Get directory contents
            try:
                items = os.listdir(current_path)
            except (OSError, PermissionError) as e:
                print(f"Cannot access directory {current_path}: {e}")
                return
                
            dirs = []
            files = []
            
            for item in items:
                item_path = os.path.join(current_path, item)
                
                try:
                    if os.path.isdir(item_path):
                        # Check if it's a symlink and if we should follow it
                        if os.path.islink(item_path):
                            if not followlinks:
                                continue
                            # Check if symlink target exists
                            if not os.path.exists(item_path):
                                continue
                        dirs.append(item)
                    elif os.path.isfile(item_path):
                        # Check for symlink files
                        if os.path.islink(item_path):
                            if not followlinks:
                                continue
                            # Check if symlink target exists
                            if not os.path.exists(item_path):
                                continue
                        files.append(item)
                except (OSError, PermissionError):
                    # Skip items we can't access
                    continue
            
            yield current_path, dirs, files
            
            # Recurse into subdirectories
            for dir_name in dirs:
                dir_path = os.path.join(current_path, dir_name)
                yield from _walk_recursive(dir_path, current_depth + 1)
                
        except Exception as e:
            print(f"Error walking directory {current_path}: {e}")
            return
    
    yield from _walk_recursive(path, 0)


def is_file_locked(filepath):
    """
    Check if a file is locked by another process.
    
    Args:
        filepath (str): Path to file to check
        
    Returns:
        bool: True if file appears to be locked
    """
    try:
        # Just try to read the file - much less intrusive than r+b
        with open(filepath, 'rb') as f:
            f.read(1)  # Try to read just one byte
        return False
    except (OSError, IOError, PermissionError):
        # File might be locked, but don't block the entire process
        return True
    except Exception:
        # If we can't determine, assume it's not locked to avoid freezing
        return False


def wait_for_file_unlock(filepath, timeout=30, check_interval=1):
    """
    Wait for a file to become unlocked.
    
    Args:
        filepath (str): Path to file
        timeout (int): Maximum time to wait in seconds
        check_interval (int): How often to check in seconds
        
    Returns:
        bool: True if file became unlocked, False if timeout
    """
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_file_locked(filepath):
            return True
        time.sleep(check_interval)
    
    return False