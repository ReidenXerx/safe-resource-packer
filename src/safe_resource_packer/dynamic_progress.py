"""
Unified Progress Display - Clean, beautiful progress tracking

This module provides a single, unified progress display system that replaces
both dynamic_progress.py and clean_output.py with one clean implementation.
"""

import os
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Global state for progress display and logging
PROGRESS_ENABLED = False
PROGRESS_LIVE = None
PROGRESS_STATS = {
    'current': 0,
    'total': 0,
    'current_file': '',
    'stage': '',
    'start_time': 0,
    'last_result': '',
    'last_update_time': 0,
    'counters': {
        'match_found': 0,
        'no_match': 0,
        'skip': 0,
        'override': 0,
        'errors': 0
    }
}
PROGRESS_LOCK = threading.Lock()

# Global state for logging
LOGS = []
SKIPPED = []
DEBUG = False

# Enhanced color mapping for beautiful logging
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

# Display update throttling (prevent flicker)
MIN_UPDATE_INTERVAL = 0.3  # Minimum 300ms between updates

# Try to import Rich for beautiful display
try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
    RICH_CONSOLE = Console()
except ImportError:
    RICH_AVAILABLE = False
    RICH_CONSOLE = None


def enable_dynamic_progress(enabled: bool = True):
    """Enable or disable progress mode."""
    global PROGRESS_ENABLED
    PROGRESS_ENABLED = enabled and RICH_AVAILABLE
    
    if PROGRESS_ENABLED:
        init_progress()


def init_progress():
    """Initialize the progress display."""
    global PROGRESS_STATS, PROGRESS_LIVE
    
    if not PROGRESS_ENABLED or not RICH_AVAILABLE:
        return
        
    # Reset progress stats
    with PROGRESS_LOCK:
        PROGRESS_STATS.update({
            'current': 0,
            'total': 0,
            'current_file': '',
            'stage': '',
            'start_time': 0,
            'last_result': '',
            'last_update_time': 0,
            'counters': {
                'match_found': 0,
                'no_match': 0,
                'skip': 0,
                'override': 0,
                'errors': 0
            }
        })
    
    # Create the live display
    PROGRESS_LIVE = None  # Will be created when needed
    
    if RICH_CONSOLE:
        RICH_CONSOLE.print()
        RICH_CONSOLE.print(Panel.fit(
            "🚀 [bold bright_white]PROGRESS MODE[/bold bright_white] 🚀\n"
            "Real-time progress tracking",
            border_style="blue"
        ))
        RICH_CONSOLE.print()


def start_dynamic_progress(stage: str, total: int, preserve_stats: bool = False):
    """Start progress tracking for a stage."""
    global PROGRESS_STATS, PROGRESS_LIVE
    
    if not PROGRESS_ENABLED or not RICH_AVAILABLE:
        return
        
    with PROGRESS_LOCK:
        # Preserve existing counters if requested
        existing_counters = PROGRESS_STATS['counters'].copy() if preserve_stats else {
            'match_found': 0,
            'no_match': 0,
            'skip': 0,
            'override': 0,
            'errors': 0
        }
        
        PROGRESS_STATS.update({
            'current': 0,
            'total': total,
            'stage': stage,
            'start_time': time.time(),
            'current_file': '',
            'last_result': '',
            'last_update_time': 0,
            'counters': existing_counters
        })
    
    # Stop any existing live display first
    if PROGRESS_LIVE:
        try:
            PROGRESS_LIVE.stop()
        except:
            pass
    
    # Create live display
    if RICH_CONSOLE:
        PROGRESS_LIVE = Live(
            _generate_progress_display(),
            console=RICH_CONSOLE,
            refresh_per_second=2,
            transient=False,
            auto_refresh=True
        )
        PROGRESS_LIVE.start()


def update_dynamic_progress(file_path: str, result: str = "", log_type: str = "", increment: bool = False):
    """Update progress with current file and result."""
    global PROGRESS_STATS, PROGRESS_LIVE
    
    if not PROGRESS_ENABLED or not PROGRESS_LIVE:
        return
    
    current_time = time.time()
    
    with PROGRESS_LOCK:
        # Throttle updates to prevent flickering
        if not increment and current_time - PROGRESS_STATS['last_update_time'] < MIN_UPDATE_INTERVAL:
            return
        
        PROGRESS_STATS['last_update_time'] = current_time
        
        if increment:
            PROGRESS_STATS['current'] += 1
        
        PROGRESS_STATS['current_file'] = os.path.basename(file_path) if file_path else ''
        PROGRESS_STATS['last_result'] = result
        
        # Update counters based on result
        # Map result types to counter names
        counter_mapping = {
            'pack': 'no_match',
            'loose': 'override',
            'skip': 'skip',
            'error': 'errors'
        }
        
        counter_name = counter_mapping.get(result, 'skip')
        if counter_name in PROGRESS_STATS['counters']:
            PROGRESS_STATS['counters'][counter_name] += 1
    
    # Update display
    if PROGRESS_LIVE:
        PROGRESS_LIVE.update(_generate_progress_display())


def finish_dynamic_progress():
    """Finish progress tracking."""
    global PROGRESS_LIVE
    
    if not PROGRESS_ENABLED or not PROGRESS_LIVE:
        return
    
    # Show final stats
    if RICH_CONSOLE:
        PROGRESS_LIVE.update(_generate_progress_display())
        time.sleep(1)  # Show final stats briefly
        PROGRESS_LIVE.stop()
        PROGRESS_LIVE = None
        
        # Show completion message
        with PROGRESS_LOCK:
            stats = PROGRESS_STATS.copy()
        
        elapsed = time.time() - stats['start_time'] if stats['start_time'] > 0 else 0
        rate = stats['current'] / elapsed if elapsed > 0 else 0
        
        RICH_CONSOLE.print(Panel.fit(
            f"✅ [bold green]Completed {stats['stage']}[/bold green]\n"
            f"Processed {stats['current']:,} files in {elapsed:.1f}s ({rate:.1f} files/s)",
            border_style="green"
        ))
        RICH_CONSOLE.print()


def _generate_progress_display():
    """Generate the progress display content."""
    if not PROGRESS_ENABLED or not RICH_AVAILABLE:
        return Text("Progress not available")
        
    with PROGRESS_LOCK:
        stats = PROGRESS_STATS.copy()
    
    current = stats['current']
    total = stats['total']
    
    if total == 0:
        return Text("Initializing...")
    
    # Calculate progress
    percent = (current * 100) // total if total > 0 else 0
    elapsed = time.time() - stats['start_time'] if stats['start_time'] > 0 else 0
    rate = current / elapsed if elapsed > 0 else 0
    eta_seconds = (total - current) / rate if rate > 0 else 0
    
    # Create progress bar
    bar_width = 30
    filled = int(bar_width * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_width - filled)
    
    # Create the display
    table = Table.grid(padding=1)
    table.add_column(style="cyan", no_wrap=True, width=12)
    table.add_column(style="white")
    
    # Progress line
    progress_line = Text()
    progress_line.append(f"🚀 {stats['stage']}: ", style="bold bright_white")
    progress_line.append(f"{current:,}/{total:,} ", style="bright_cyan")
    progress_line.append(f"({percent}%) ", style="bright_yellow")
    progress_line.append(f"[{bar}] ", style="bright_blue")
    
    if rate > 0:
        progress_line.append(f"{rate:.1f}/s ", style="dim bright_white")
        if eta_seconds < 3600:
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            progress_line.append(f"ETA: {eta_min}m{eta_sec:02d}s", style="dim bright_green")
    
    table.add_row("Progress:", progress_line)
    
    # Current file line
    if stats['current_file']:
        current_file_display = stats['current_file']
        if len(current_file_display) > 50:
            current_file_display = "..." + current_file_display[-47:]
        table.add_row("Current:", f"[cyan]{current_file_display}[/cyan]")
    
    # Stats line
    counters = stats['counters']
    stats_line = Text()
    stats_line.append(f"🎯 {counters['match_found']} ", style="bright_green")
    stats_line.append(f"📦 {counters['no_match']} ", style="bright_blue")
    stats_line.append(f"🔄 {counters['override']} ", style="bright_magenta")
    stats_line.append(f"⏭️ {counters['skip']} ", style="bright_yellow")
    if counters['errors'] > 0:
        stats_line.append(f"❌ {counters['errors']} ", style="bright_red")
    
    table.add_row("Stats:", stats_line)
    
    return table


def is_dynamic_progress_enabled() -> bool:
    """Check if progress mode is enabled."""
    return PROGRESS_ENABLED


# Backward compatibility aliases
def update_dynamic_progress_with_counts(file_path: str, result: str = "", log_type: str = "", **kwargs):
    """Backward compatibility wrapper."""
    update_dynamic_progress(file_path, result, log_type, increment=True)


def set_dynamic_progress_current(current: int):
    """Set current progress count."""
    global PROGRESS_STATS
    with PROGRESS_LOCK:
        PROGRESS_STATS['current'] = current


def handle_dynamic_progress_log(message: str, log_type: str):
    """Handle progress log messages."""
    if not PROGRESS_ENABLED:
        return False
    
    # Extract file path from message if possible
    file_path = ""
    if "Processing:" in message:
        file_path = message.split("Processing:")[-1].strip()
    
    update_dynamic_progress(file_path, log_type, increment=False)
    return True


# Clean Output Manager (replaces clean_output.py)
class CleanOutputManager:
    """Unified progress manager that replaces both progress systems."""
    
    def __init__(self, console: Optional[Console] = None, quiet: bool = False):
        """Initialize the clean output manager."""
        self.console = console or RICH_CONSOLE
        self.quiet = quiet
        self.stats = {
            'match_found': 0,
            'no_match': 0,
            'skip': 0,
            'override': 0,
            'errors': 0,
            'current_file': '',
            'total_files': 0,
            'processed': 0,
            'start_time': time.time()
        }
        
    def start_processing(self, total_files: int):
        """Start the processing display."""
        self.stats['total_files'] = total_files
        self.stats['start_time'] = time.time()
        
        if not RICH_AVAILABLE or self.quiet:
            if not self.quiet:
                print(f"🔄 Processing {total_files} files...")
            return
        
        # Use the unified progress system
        start_dynamic_progress("Processing", total_files)
    
    def update_progress(self, current_file: str, result_type: str):
        """Update progress with current file and result."""
        self.stats['processed'] += 1
        self.stats['current_file'] = current_file
        
        # Map result types to counter names
        counter_mapping = {
            'pack': 'no_match',
            'loose': 'override',
            'skip': 'skip',
            'error': 'errors'
        }
        
        counter_name = counter_mapping.get(result_type, 'skip')
        if counter_name in self.stats:
            self.stats[counter_name] += 1
        
        if not RICH_AVAILABLE or self.quiet:
            if not self.quiet:
                # Simple progress for non-rich mode
                percent = (self.stats['processed'] / self.stats['total_files']) * 100
                status_icon = {
                    'pack': '📦',
                    'loose': '🔄', 
                    'skip': '⏭️',
                    'error': '❌'
                }.get(result_type, '🔄')
                
                print(f"\r{status_icon} [{percent:5.1f}%] {current_file[:50]:<50}", end='', flush=True)
            return
        
        # Use the unified progress system
        update_dynamic_progress(current_file, result_type, increment=True)
    
    def finish_processing(self):
        """Finish the processing display."""
        if not self.quiet:
            print()  # New line after progress
        
        # Use the unified progress system
        finish_dynamic_progress()


def create_clean_progress_callback(console: Optional[Console] = None, quiet: bool = False):
    """Create a clean progress callback for the classifier."""
    if RICH_AVAILABLE and not quiet and console:
        return CleanOutputManager(console, quiet)
    else:
        return SimpleProgressCallback(quiet)


class SimpleProgressCallback:
    """Simple progress callback for basic mode."""
    
    def __init__(self, quiet: bool = False):
        """Initialize simple progress callback."""
        self.quiet = quiet
        self.last_update = 0
        self.update_interval = 0.1
    
    def __call__(self, current: int, total: int, stage: str, extra: str = ""):
        """Progress callback function."""
        if self.quiet:
            return
        
        current_time = time.time()
        if current_time - self.last_update < self.update_interval and current < total:
            return
        
        self.last_update = current_time
        
        # Determine status icon
        if "pack" in extra.lower():
            icon = "📦"
        elif "loose" in extra.lower():
            icon = "📁"
        elif "skip" in extra.lower():
            icon = "⏭️"
        elif "error" in extra.lower():
            icon = "❌"
        else:
            icon = "🔄"
        
        # Clean file name display
        filename = Path(extra).name if extra else ""
        if len(filename) > 40:
            filename = "..." + filename[-37:]
        
        percent = (current / max(total, 1)) * 100
        bar_length = 30
        filled_length = int(bar_length * current // max(total, 1))
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Clean, colorful output
        import sys
        sys.stdout.write(f"\r{icon} [{bar}] {percent:5.1f}% {filename:<40}")
        sys.stdout.flush()
        
        if current >= total:
            print()  # New line when complete


def enhance_classifier_output(classifier, quiet: bool = False):
    """Enhance classifier output to be cleaner and prettier."""
    # Store original process_file method
    original_process_file = classifier.process_file
    
    def clean_process_file(*args, **kwargs):
        """Wrapper for process_file with cleaner output."""
        result, path = original_process_file(*args, **kwargs)
        
        # Only log significant events, not every file
        if not quiet and result in ['loose', 'error']:
            if result == 'loose':
                print(f"📁 Override: {Path(path).name}")
            elif result == 'error':
                print(f"❌ Error: {Path(path).name}")
        
        return result, path
    
    # Replace the method
    classifier.process_file = clean_process_file
    return classifier


# Logging functions (consolidated from utils.py)
def set_debug(debug_mode, dynamic_progress=True, table_view=False):
    """Set global debug mode with modern dynamic progress display."""
    global DEBUG
    DEBUG = debug_mode
    
    # Enable dynamic progress system
    if debug_mode:
        enable_dynamic_progress(dynamic_progress and not table_view)


def log(message, debug_only=False, quiet_mode=False, log_type=None):
    """
    Log a message with timestamp and optional coloring.
    Now supports dynamic progress mode to eliminate spam!

    Args:
        message (str): Message to log
        debug_only (bool): Only log if debug mode is enabled
        quiet_mode (bool): Suppress console output if quiet mode
        log_type (str): Type of log for coloring (e.g., 'MATCH FOUND', 'SKIP', etc.)
    """
    if debug_only and not DEBUG:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with PROGRESS_LOCK:
        LOGS.append(f"[{timestamp}] {message}")

    # Handle dynamic progress for classification messages (NO SPAM!)
    if debug_only and log_type:
        if handle_dynamic_progress_log(message, log_type):
            return  # Message handled by dynamic progress, no console spam!

    # Only print to console if not in quiet mode
    if not quiet_mode:
        if RICH_AVAILABLE and DEBUG and log_type:
            # Beautiful colored output for debug mode
            _print_colored_log(timestamp, message, log_type)
        else:
            # Regular output
            print(f"[{timestamp}] {message}")


def _print_colored_log(timestamp, message, log_type):
    """Print colored log message using Rich."""
    if not RICH_AVAILABLE:
        print(f"[{timestamp}] {message}")
        return
    
    icon = LOG_ICONS.get(log_type, "💡")
    color = LOG_COLORS.get(log_type, "white")
    
    RICH_CONSOLE.print(f"[{timestamp}] {icon} ", end="")
    RICH_CONSOLE.print(f"[{color}]{message}[/{color}]")


def get_logs():
    """Get all logs."""
    with PROGRESS_LOCK:
        return LOGS.copy()


def get_skipped():
    """Get all skipped files."""
    with PROGRESS_LOCK:
        return SKIPPED.copy()


def clear_logs():
    """Clear all logs and skipped files."""
    global LOGS, SKIPPED
    with PROGRESS_LOCK:
        LOGS = []
        SKIPPED = []


def write_log_file(path):
    """Write logs to file."""
    with PROGRESS_LOCK:
        logs = LOGS.copy()
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            for log_entry in logs:
                f.write(log_entry + '\n')
    except Exception as e:
        print(f"Failed to write log file: {e}")


def log_classification_progress(current, total, current_file=""):
    """Log classification progress (legacy compatibility)."""
    if not DEBUG:
        return
    
    percent = (current / max(total, 1)) * 100
    log(f"Classification progress: {current}/{total} ({percent:.1f}%) - {current_file}", 
        debug_only=True, log_type='CLASSIFYING')


def print_progress(current, total, stage, extra="", callback=None):
    """Print progress (legacy compatibility)."""
    if callback:
        callback(current, total, stage, extra)
    else:
        log_classification_progress(current, total, extra)