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

# Global state for table-based debug view
DEBUG_TABLE_ENTRIES = []
DEBUG_TABLE_LIVE = None
DEBUG_TABLE_ENABLED = False
DEBUG_TABLE_INITIALIZED = False
CLASSIFICATION_STATS = {
    'total': 0,
    'processed': 0,
    'match_found': 0,
    'no_match': 0,
    'skip': 0,
    'override': 0,
    'errors': 0
}

# Check if rich is available for colored output
try:
    from rich.console import Console
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.columns import Columns
    RICH_CONSOLE = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_CONSOLE = None
    RICH_AVAILABLE = False

# Enhanced color mapping for beautiful classification logging
LOG_COLORS = {
    'MATCH FOUND': 'bright_green',
    'NO MATCH': 'bright_blue',
    'SKIP': 'bright_yellow',
    'OVERRIDE': 'bright_magenta',
    'LOOSE FAIL': 'bright_red',
    'COPY FAIL': 'red',
    'HASH FAIL': 'red',
    'EXCEPTION': 'red',
    'ERROR': 'red',
    'SUCCESS': 'bright_green',
    'INFO': 'bright_cyan',
    'WARNING': 'yellow',
    'CLASSIFYING': 'bright_white',
    'PATH_EXTRACT': 'cyan',
    'FILENAME_SANITIZED': 'yellow'
}

# Beautiful icons for different log types
LOG_ICONS = {
    'MATCH FOUND': '🎯',
    'NO MATCH': '📦',
    'SKIP': '⏭️',
    'OVERRIDE': '🔄',
    'LOOSE FAIL': '⚠️',
    'COPY FAIL': '❌',
    'HASH FAIL': '💥',
    'EXCEPTION': '⚠️',
    'ERROR': '❌',
    'SUCCESS': '✅',
    'INFO': '💡',
    'WARNING': '⚠️',
    'CLASSIFYING': '⚡',
    'PATH_EXTRACT': '🔍',
    'FILENAME_SANITIZED': '🧹'
}


def set_debug(debug_mode, table_view=False):
    """Set global debug mode and optionally enable table view."""
    global DEBUG, DEBUG_TABLE_ENABLED
    DEBUG = debug_mode
    DEBUG_TABLE_ENABLED = debug_mode and table_view and RICH_AVAILABLE
    
    if DEBUG_TABLE_ENABLED:
        init_debug_table()

def init_debug_table():
    """Initialize the debug table view."""
    global DEBUG_TABLE_ENTRIES, CLASSIFICATION_STATS, DEBUG_TABLE_INITIALIZED
    
    if not RICH_AVAILABLE or DEBUG_TABLE_INITIALIZED:
        return
        
    # Reset table data
    DEBUG_TABLE_ENTRIES = []
    CLASSIFICATION_STATS = {
        'total': 0,
        'processed': 0,
        'match_found': 0,
        'no_match': 0,
        'skip': 0,
        'override': 0,
        'errors': 0
    }
    
    # Print initial table header only once
    RICH_CONSOLE.print()
    RICH_CONSOLE.print(Panel.fit(
        "🎯 [bold bright_white]CLASSIFICATION DEBUG TABLE[/bold bright_white] 🎯",
        style="bright_cyan"
    ))
    RICH_CONSOLE.print()
    
    DEBUG_TABLE_INITIALIZED = True

def add_debug_table_entry(file_path: str, action: str, result: str, details: str = ""):
    """Add an entry to the debug table."""
    global DEBUG_TABLE_ENTRIES, CLASSIFICATION_STATS
    
    if not DEBUG_TABLE_ENABLED:
        return
        
    with LOCK:
        # Update stats
        CLASSIFICATION_STATS['processed'] += 1
        
        action_lower = action.lower()
        if 'match found' in action_lower:
            CLASSIFICATION_STATS['match_found'] += 1
        elif 'no match' in action_lower:
            CLASSIFICATION_STATS['no_match'] += 1
        elif 'skip' in action_lower:
            CLASSIFICATION_STATS['skip'] += 1
        elif 'override' in action_lower:
            CLASSIFICATION_STATS['override'] += 1
        elif 'error' in action_lower or 'fail' in action_lower:
            CLASSIFICATION_STATS['errors'] += 1
        
        # Add entry (keep only last 20 for performance)
        entry = {
            'file': os.path.basename(file_path),
            'action': action,
            'result': result,
            'details': details,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        DEBUG_TABLE_ENTRIES.append(entry)
        if len(DEBUG_TABLE_ENTRIES) > 20:
            DEBUG_TABLE_ENTRIES.pop(0)
        
        # Print updated table much less frequently to avoid spam
        if (CLASSIFICATION_STATS['processed'] % 50 == 0 or 
            action.upper() in ['ERROR'] or  # Only on errors, not every match
            CLASSIFICATION_STATS['processed'] <= 10):  # Show first 10 for feedback
            print_debug_table()

def print_debug_table():
    """Print the current debug table - simplified to avoid spam."""
    if not DEBUG_TABLE_ENABLED or not DEBUG_TABLE_ENTRIES:
        return
        
    # Only show a simple progress update instead of full table
    stats = CLASSIFICATION_STATS
    
    # Create a simple one-line progress update
    progress_text = (
        f"📊 Progress: {stats['processed']:,} processed | "
        f"🎯 {stats['match_found']:,} matches | "
        f"📦 {stats['no_match']:,} new | "
        f"⏭️ {stats['skip']:,} skipped | "
        f"🔄 {stats['override']:,} overrides"
    )
    
    if stats['errors'] > 0:
        progress_text += f" | ❌ {stats['errors']:,} errors"
    
    # Show last processed file
    if DEBUG_TABLE_ENTRIES:
        last_entry = DEBUG_TABLE_ENTRIES[-1]
        file_info = f" | Currently: {last_entry['file']}"
        progress_text += file_info
    
    RICH_CONSOLE.print(f"\r{progress_text}", end="")
    
    # Only show full table on major milestones
    if (stats['processed'] > 0 and 
        (stats['processed'] % 500 == 0 or stats['errors'] > 0)):
        _print_full_table()

def _print_full_table():
    """Print the full debug table for major milestones."""
    if not DEBUG_TABLE_ENABLED or not DEBUG_TABLE_ENTRIES:
        return
    
    RICH_CONSOLE.print("\n")  # New line after progress
    
    # Create simplified table
    table = Table(show_header=True, header_style="bold bright_white", box=None)
    table.add_column("File", style="bright_cyan", width=35, no_wrap=True)
    table.add_column("Action", width=12, no_wrap=True)
    table.add_column("Result", width=8, no_wrap=True)
    
    # Show last 5 entries only
    for entry in DEBUG_TABLE_ENTRIES[-5:]:
        # Style action based on type
        action_text = Text(entry['action'])
        if 'MATCH FOUND' in entry['action']:
            action_text.stylize("bold bright_green")
        elif 'NO MATCH' in entry['action']:
            action_text.stylize("bold bright_blue")
        elif 'SKIP' in entry['action']:
            action_text.stylize("bold bright_yellow")
        elif 'OVERRIDE' in entry['action']:
            action_text.stylize("bold bright_magenta")
        elif 'ERROR' in entry['action']:
            action_text.stylize("bold red")
            
        # Style result
        result_text = Text(entry['result'])
        if entry['result'].upper() == 'PACK':
            result_text.stylize("bright_blue")
        elif entry['result'].upper() == 'LOOSE':
            result_text.stylize("bright_magenta")
        elif entry['result'].upper() == 'SKIP':
            result_text.stylize("bright_yellow")
        elif entry['result'].upper() == 'ERROR':
            result_text.stylize("red")
            
        table.add_row(
            entry['file'][:33] + "..." if len(entry['file']) > 33 else entry['file'],
            action_text,
            result_text
        )
    
    RICH_CONSOLE.print(table)
    RICH_CONSOLE.print()

def set_debug_table_total(total: int):
    """Set the total number of files to process."""
    global CLASSIFICATION_STATS
    if DEBUG_TABLE_ENABLED:
        with LOCK:
            CLASSIFICATION_STATS['total'] = total

def finish_debug_table():
    """Print final debug table summary."""
    if not DEBUG_TABLE_ENABLED:
        return
        
    stats = CLASSIFICATION_STATS
    
    # Create final summary
    summary_text = (
        f"✅ [bold bright_green]CLASSIFICATION COMPLETE![/bold bright_green]\n\n"
        f"📊 [bold bright_white]FINAL STATISTICS:[/bold bright_white]\n"
        f"[bright_cyan]Total Files:[/bright_cyan] {stats['total']:,}\n"
        f"[bright_cyan]Processed:[/bright_cyan] {stats['processed']:,} files\n"
        f"[bright_green]Found Matches:[/bright_green] {stats['match_found']:,}\n"
        f"[bright_blue]New Files (Pack):[/bright_blue] {stats['no_match']:,}\n"
        f"[bright_yellow]Identical (Skip):[/bright_yellow] {stats['skip']:,}\n"
        f"[bright_magenta]Overrides (Loose):[/bright_magenta] {stats['override']:,}\n"
        f"[red]Errors:[/red] {stats['errors']:,}\n\n"
        f"🎉 [bold bright_white]Processing completed successfully![/bold bright_white]"
    )
    
    RICH_CONSOLE.print()
    RICH_CONSOLE.print(Panel(summary_text, title="🎯 Final Results", style="bright_green"))
    RICH_CONSOLE.print()
    
    # Reset the debug table state for next run
    reset_debug_table()

def reset_debug_table():
    """Reset debug table state."""
    global DEBUG_TABLE_INITIALIZED, DEBUG_TABLE_ENTRIES, CLASSIFICATION_STATS
    DEBUG_TABLE_INITIALIZED = False
    DEBUG_TABLE_ENTRIES = []
    CLASSIFICATION_STATS = {
        'total': 0,
        'processed': 0,
        'match_found': 0,
        'no_match': 0,
        'skip': 0,
        'override': 0,
        'errors': 0
    }


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
        # Removed log size management - it was causing recursive loops and freezing
        # For single session usage, memory growth is not a real issue

    # Handle table view for classification messages
    if DEBUG_TABLE_ENABLED and log_type and debug_only:
        _handle_table_log(message, log_type)
        return  # Don't print individual messages when table view is active

    # Only print to console if not in quiet mode
    if not quiet_mode:
        if RICH_AVAILABLE and DEBUG and log_type:
            # Beautiful colored output for debug mode
            _print_colored_log(timestamp, message, log_type)
        else:
            # Regular output
            print(f"[{timestamp}] {message}")

def _handle_table_log(message: str, log_type: str):
    """Handle logging for table view."""
    if not DEBUG_TABLE_ENABLED:
        return
        
    # Extract file path and details from common log message patterns
    file_path = ""
    result = ""
    details = ""
    
    if log_type == 'MATCH FOUND' and ' matched to ' in message:
        parts = message.split(' matched to ')
        if len(parts) == 2:
            file_path = parts[0].replace('[MATCH FOUND] ', '')
            result = "SKIP"  # Will be overridden by actual classification
            details = os.path.basename(parts[1])
    elif log_type == 'NO MATCH' and ' → ' in message:
        parts = message.split(' → ')
        if len(parts) == 2:
            file_path = parts[0].replace('[NO MATCH] ', '')
            result = parts[1].upper()
            details = "New file"
    elif log_type == 'SKIP' and ' identical' in message:
        file_path = message.replace('[SKIP] ', '').replace(' identical', '')
        result = "SKIP"
        details = "Unchanged"
    elif log_type == 'OVERRIDE' and ' differs' in message:
        file_path = message.replace('[OVERRIDE] ', '').replace(' differs', '')
        result = "LOOSE"
        details = "Modified"
    elif 'Classifying' in message:
        file_path = message.replace('Classifying ', '')
        result = "..."
        details = "Processing"
        log_type = "CLASSIFYING"
    else:
        # Generic handling
        file_path = message[:50]  # First 50 chars
        result = log_type
        details = ""
    
    if file_path:
        add_debug_table_entry(file_path, log_type, result, details)


def _print_colored_log(timestamp, message, log_type):
    """Print a beautiful, sexy colored log message using Rich."""
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

    # Create beautiful timestamp with gradient effect
    timestamp_text = Text(f"[{timestamp}]", style="dim bright_black")

    # Enhanced message formatting based on log type
    if log_type == 'MATCH FOUND':
        # Beautiful match found format: 🎯 [MATCH FOUND] filename.nif matched to source/path
        parts = message.split(' matched to ')
        if len(parts) == 2:
            file_part = parts[0].replace('[MATCH FOUND] ', '')
            source_part = parts[1]
            message_text = Text()
            message_text.append(f"{icon} ", style="bright_green")
            message_text.append("[MATCH FOUND] ", style="bold bright_green")
            message_text.append(file_part, style="bright_white")
            message_text.append(" → ", style="dim bright_green")
            message_text.append(source_part, style="dim cyan")
        else:
            message_text = Text(f"{icon} {message}", style=color)
    
    elif log_type == 'NO MATCH':
        # Beautiful no match format: 📦 [NO MATCH] filename.nif → pack
        parts = message.split(' → ')
        if len(parts) == 2:
            file_part = parts[0].replace('[NO MATCH] ', '')
            action_part = parts[1]
            message_text = Text()
            message_text.append(f"{icon} ", style="bright_blue")
            message_text.append("[NO MATCH] ", style="bold bright_blue")
            message_text.append(file_part, style="bright_white")
            message_text.append(" → ", style="dim bright_blue")
            message_text.append(action_part.upper(), style="bold bright_blue")
        else:
            message_text = Text(f"{icon} {message}", style=color)
    
    elif log_type == 'SKIP':
        # Beautiful skip format: ⏭️ [SKIP] filename.nif identical
        file_part = message.replace('[SKIP] ', '').replace(' identical', '')
        message_text = Text()
        message_text.append(f"{icon} ", style="bright_yellow")
        message_text.append("[SKIP] ", style="bold bright_yellow")
        message_text.append(file_part, style="bright_white")
        message_text.append(" identical", style="dim bright_yellow")
    
    elif log_type == 'OVERRIDE':
        # Beautiful override format: 🔄 [OVERRIDE] filename.nif differs
        file_part = message.replace('[OVERRIDE] ', '').replace(' differs', '')
        message_text = Text()
        message_text.append(f"{icon} ", style="bright_magenta")
        message_text.append("[OVERRIDE] ", style="bold bright_magenta")
        message_text.append(file_part, style="bright_white")
        message_text.append(" differs", style="dim bright_magenta")
    
    elif log_type == 'PATH_EXTRACT':
        # Beautiful path extraction: 🔍 Found game dir 'meshes': long/path → meshes/relative/path
        if '→' in message:
            parts = message.split(' → ')
            if len(parts) == 2:
                source_part = parts[0]
                result_part = parts[1]
                message_text = Text()
                message_text.append(f"{icon} ", style="cyan")
                message_text.append(source_part, style="dim cyan")
                message_text.append(" → ", style="bright_cyan")
                message_text.append(result_part, style="bold bright_white")
            else:
                message_text = Text(f"{icon} {message}", style=color)
        else:
            message_text = Text(f"{icon} {message}", style=color)
    
    elif 'Classifying' in message:
        # Beautiful classifying progress: ⚡ Classifying meshes/actors/character/body.nif
        file_part = message.replace('Classifying ', '')
        message_text = Text()
        message_text.append("⚡ ", style="bright_white")
        message_text.append("Classifying ", style="bold bright_white")
        message_text.append(file_part, style="bright_cyan")
    
    else:
        # Default beautiful format
        if log_type and f"[{log_type}]" in message:
            # Replace the log type with beautiful colored version
            colored_message = message.replace(f"[{log_type}]", "")
            message_text = Text()
            message_text.append(f"{icon} ", style=color)
            message_text.append(f"[{log_type}] ", style=f"bold {color}")
            message_text.append(colored_message, style="bright_white")
        else:
            message_text = Text(f"{icon} {message}", style=color)

    # Print with beautiful spacing and alignment
    RICH_CONSOLE.print(timestamp_text, " ", message_text, end="")
    RICH_CONSOLE.print()  # Add newline


def log_classification_progress(current, total, current_file=""):
    """Log beautiful classification progress with file info."""
    if RICH_AVAILABLE and DEBUG and current_file:
        percentage = (current / total * 100) if total > 0 else 0
        progress_text = Text()
        progress_text.append(f"⚡ ", style="bright_white")
        progress_text.append(f"[{current:,}/{total:,}] ", style="bold bright_cyan")
        progress_text.append(f"{percentage:.1f}% ", style="bright_yellow")
        progress_text.append("│ ", style="dim white")
        progress_text.append("Classifying ", style="bold bright_white")
        progress_text.append(current_file, style="bright_cyan")
        RICH_CONSOLE.print(progress_text)


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
        if file_size > 8 * 1024 * 1024 * 1024:  # 8GB limit (much more generous)
            log(f"[HASH WARNING] Very large file detected: {path} ({file_size / (1024**3):.1f}GB)", 
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


# Removed manage_log_size function - it was causing recursive loops and freezing
# For single session usage, unlimited log growth is acceptable


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
