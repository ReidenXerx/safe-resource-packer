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


# Global state for logging
LOGS = []
SKIPPED = []
LOCK = threading.Lock()
DEBUG = False

# Check if rich is available for colored output
try:
    from rich.console import Console
    from rich.text import Text
    RICH_CONSOLE = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_CONSOLE = None
    RICH_AVAILABLE = False

# Color mapping for different log types
LOG_COLORS = {
    'MATCH FOUND': 'green',
    'NO MATCH': 'blue',
    'SKIP': 'yellow',
    'OVERRIDE': 'magenta',
    'LOOSE FAIL': 'red',
    'COPY FAIL': 'red',
    'HASH FAIL': 'red',
    'EXCEPTION': 'red',
    'ERROR': 'red',
    'SUCCESS': 'green',
    'INFO': 'cyan',
    'WARNING': 'yellow'
}

# Icons for different log types
LOG_ICONS = {
    'MATCH FOUND': '🔍',
    'NO MATCH': '📦',
    'SKIP': '⏭️',
    'OVERRIDE': '📁',
    'LOOSE FAIL': '⚠️',
    'COPY FAIL': '❌',
    'HASH FAIL': '💥',
    'EXCEPTION': '⚠️',
    'ERROR': '❌',
    'SUCCESS': '✅',
    'INFO': 'ℹ️',
    'WARNING': '⚠️'
}


def set_debug(debug_mode):
    """Set global debug mode."""
    global DEBUG
    DEBUG = debug_mode


def log(message, debug_only=False, quiet_mode=False, log_type=None):
    """
    Log a message with timestamp and optional coloring.

    Args:
        message (str): Message to log
        debug_only (bool): Only log if debug mode is enabled
        quiet_mode (bool): Suppress console output if quiet mode
        log_type (str): Type of log for coloring (e.g., 'MATCH FOUND', 'SKIP', etc.)
    """
    if debug_only and not DEBUG:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOCK:
        LOGS.append(f"[{timestamp}] {message}")
        
        # Manage log size to prevent memory issues
        if len(LOGS) % 1000 == 0:  # Check every 1000 entries
            manage_log_size()

    # Only print to console if not in quiet mode
    if not quiet_mode:
        if RICH_AVAILABLE and DEBUG and log_type:
            # Beautiful colored output for debug mode
            _print_colored_log(timestamp, message, log_type)
        else:
            # Regular output
            print(f"[{timestamp}] {message}")


def _print_colored_log(timestamp, message, log_type):
    """Print a colored log message using Rich."""
    if not RICH_CONSOLE:
        print(f"[{timestamp}] {message}")
        return

    # Extract the log type from the message if not provided
    if not log_type:
        for key in LOG_COLORS.keys():
            if key in message:
                log_type = key
                break

    # Get color and icon
    color = LOG_COLORS.get(log_type, 'white')
    icon = LOG_ICONS.get(log_type, '•')

    # Create colored timestamp
    timestamp_text = Text(f"[{timestamp}]", style="dim cyan")

    # Create colored message with icon
    if log_type in message:
        # Replace the log type with colored version
        colored_message = message.replace(f"[{log_type}]", f"{icon} [{log_type}]")
        message_text = Text(colored_message, style=color)
    else:
        message_text = Text(f"{icon} {message}", style=color)

    # Print with rich console
    RICH_CONSOLE.print(timestamp_text, message_text)


def print_progress(current, total, stage, extra="", callback=None):
    """
    Print a progress bar.

    Args:
        current (int): Current progress
        total (int): Total items
        stage (str): Current stage description
        extra (str): Extra information to display
        callback (callable): Optional callback for enhanced progress display
    """
    if callback:
        callback(current, total, stage, extra)
        return

    bar_len = 40
    filled_len = int(round(bar_len * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write(f"\r[{bar}] {percents}% | {stage} {extra}   ")
    sys.stdout.flush()

    # If this is the last item, add a newline to separate from next output
    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


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
        if file_size > 4 * 1024 * 1024 * 1024:  # 4GB limit
            log(f"[HASH WARNING] Large file detected: {path} ({file_size / (1024**3):.1f}GB)", 
                debug_only=True, log_type='WARNING')
        
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
        # Handle specific OS errors (permissions, disk issues, etc.)
        with LOCK:
            SKIPPED.append(f"[HASH FAIL] {path}: OS Error - {e}")
        log(f"[HASH FAIL] {path}: OS Error - {e}", debug_only=True, log_type='HASH FAIL')
        return None
    except MemoryError as e:
        # Handle memory exhaustion
        with LOCK:
            SKIPPED.append(f"[HASH FAIL] {path}: Memory exhausted - {e}")
        log(f"[HASH FAIL] {path}: Memory exhausted - {e}", debug_only=True, log_type='HASH FAIL')
        return None
    except Exception as e:
        with LOCK:
            SKIPPED.append(f"[HASH FAIL] {path}: {e}")
        log(f"[HASH FAIL] {path}: {e}", debug_only=True, log_type='HASH FAIL')
        return None


def write_log_file(path):
    """
    Write all logs to a file.

    Args:
        path (str): Path to log file
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            with LOCK:
                f.write('\n'.join(LOGS))
                if SKIPPED:
                    f.write('\n\n[SKIPPED FILES]\n')
                    f.write('\n'.join(SKIPPED))
        log(f"Log written to {path}")
    except Exception as e:
        print(f"Failed to write log file: {e}")


def get_logs():
    """Get copy of all logs."""
    with LOCK:
        return LOGS.copy()


def get_skipped():
    """Get copy of all skipped files."""
    with LOCK:
        return SKIPPED.copy()


def clear_logs():
    """Clear all logs and skipped files."""
    global LOGS, SKIPPED
    with LOCK:
        LOGS = []
        SKIPPED = []


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
        # Windows has stricter limits
        max_length = 260 if platform.system() == 'Windows' else 4096
    
    if len(path) > max_length:
        return False, f"Path too long: {len(path)} chars (max {max_length})"
    
    # Check for invalid characters
    if platform.system() == 'Windows':
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            if char in path:
                return False, f"Invalid character '{char}' in path"
        
        # Check for reserved names
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                         'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                         'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                         'LPT7', 'LPT8', 'LPT9'}
        
        filename = os.path.basename(path).split('.')[0].upper()
        if filename in reserved_names:
            return False, f"Reserved filename '{filename}' not allowed on Windows"
    
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
        log(f"Failed to check disk space for {path}: {e}", log_type='WARNING')
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


def manage_log_size(max_entries=10000):
    """
    Manage log size to prevent memory issues.
    
    Args:
        max_entries (int): Maximum number of log entries to keep
    """
    global LOGS, SKIPPED
    with LOCK:
        if len(LOGS) > max_entries:
            # Keep only the most recent entries
            LOGS = LOGS[-max_entries:]
            log(f"Log trimmed to {max_entries} entries", log_type='INFO')
        
        if len(SKIPPED) > max_entries:
            SKIPPED = SKIPPED[-max_entries:]


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
            log(f"Max depth {max_depth} reached, stopping walk at: {current_path}", 
                log_type='WARNING')
            return
            
        try:
            # Resolve path to detect circular references
            real_path = os.path.realpath(current_path)
            if real_path in visited:
                log(f"Circular reference detected, skipping: {current_path}", 
                    debug_only=True, log_type='WARNING')
                return
            visited.add(real_path)
            
            # Check if path is accessible
            if not os.path.exists(current_path) or not os.path.isdir(current_path):
                return
                
            # Get directory contents
            try:
                items = os.listdir(current_path)
            except (OSError, PermissionError) as e:
                log(f"Cannot access directory {current_path}: {e}", 
                    debug_only=True, log_type='WARNING')
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
                                log(f"Skipping symlink directory: {item_path}", 
                                    debug_only=True, log_type='INFO')
                                continue
                            # Check if symlink target exists
                            if not os.path.exists(item_path):
                                log(f"Broken symlink detected: {item_path}", 
                                    debug_only=True, log_type='WARNING')
                                continue
                        dirs.append(item)
                    elif os.path.isfile(item_path):
                        # Check for symlink files
                        if os.path.islink(item_path):
                            if not followlinks:
                                log(f"Skipping symlink file: {item_path}", 
                                    debug_only=True, log_type='INFO')
                                continue
                            # Check if symlink target exists
                            if not os.path.exists(item_path):
                                log(f"Broken symlink detected: {item_path}", 
                                    debug_only=True, log_type='WARNING')
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
            log(f"Error walking directory {current_path}: {e}", 
                debug_only=True, log_type='ERROR')
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
        # Try to open file for reading and writing
        with open(filepath, 'r+b') as f:
            pass
        return False
    except (OSError, IOError, PermissionError):
        return True
    except Exception:
        # If we can't determine, assume it's not locked
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
