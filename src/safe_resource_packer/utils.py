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


def set_debug(debug_mode):
    """Set global debug mode."""
    global DEBUG
    DEBUG = debug_mode


def log(message, debug_only=False):
    """
    Log a message with timestamp.

    Args:
        message (str): Message to log
        debug_only (bool): Only log if debug mode is enabled
    """
    if debug_only and not DEBUG:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOCK:
        LOGS.append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")


def print_progress(current, total, stage, extra=""):
    """
    Print a progress bar.

    Args:
        current (int): Current progress
        total (int): Total items
        stage (str): Current stage description
        extra (str): Extra information to display
    """
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
