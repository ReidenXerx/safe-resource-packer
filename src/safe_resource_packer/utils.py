"""
Utility functions for Safe Resource Packer.
"""

import os
import sys
import hashlib
import threading
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


def file_hash(path):
    """
    Calculate SHA1 hash of a file.

    Args:
        path (str): Path to file

    Returns:
        str or None: SHA1 hash or None if error
    """
    try:
        with open(path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
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
