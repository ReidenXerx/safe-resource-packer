"""
Dynamic Progress Display - Eliminates debug logging spam!

This module provides a beautiful, real-time single-line progress display
that replaces the annoying spam of individual debug log messages.
"""

import os
import time
import threading
from typing import Optional

# Global state for dynamic progress display
DYNAMIC_PROGRESS_ENABLED = False
DYNAMIC_PROGRESS_LIVE = None
DYNAMIC_PROGRESS_STATS = {
    'current': 0,
    'total': 0,
    'current_file': '',
    'stage': '',
    'start_time': 0,
    'last_result': '',
    'last_update_time': 0,  # Add throttling timestamp
    'counters': {
        'match_found': 0,
        'no_match': 0,
        'skip': 0,
        'override': 0,
        'errors': 0
    }
}
PROGRESS_LOCK = threading.Lock()

# Display update throttling (prevent flicker)
MIN_UPDATE_INTERVAL = 0.3  # Minimum 300ms between updates (3.3 FPS max)

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
    """Enable or disable dynamic progress mode."""
    global DYNAMIC_PROGRESS_ENABLED
    DYNAMIC_PROGRESS_ENABLED = enabled and RICH_AVAILABLE
    
    if DYNAMIC_PROGRESS_ENABLED:
        init_dynamic_progress()


def init_dynamic_progress():
    """Initialize the dynamic progress display."""
    global DYNAMIC_PROGRESS_STATS, DYNAMIC_PROGRESS_LIVE
    
    if not DYNAMIC_PROGRESS_ENABLED or not RICH_AVAILABLE:
        return
        
    # Reset progress stats
    with PROGRESS_LOCK:
        DYNAMIC_PROGRESS_STATS.update({
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
    DYNAMIC_PROGRESS_LIVE = None  # Will be created when needed
    
    if RICH_CONSOLE:
        RICH_CONSOLE.print()
        RICH_CONSOLE.print(Panel.fit(
            "🚀 [bold bright_white]DYNAMIC PROGRESS MODE[/bold bright_white] 🚀\n"
            "Real-time single-line updates (no spam!)",
            style="bright_cyan"
        ))
        RICH_CONSOLE.print()


def start_dynamic_progress(stage: str, total: int, preserve_stats: bool = False):
    """Start dynamic progress tracking for a stage.
    
    Args:
        stage: Name of the stage (e.g., "Classification", "Compression")
        total: Total number of items to process
        preserve_stats: If True, keep existing counter stats (useful for compression phase)
    """
    global DYNAMIC_PROGRESS_STATS, DYNAMIC_PROGRESS_LIVE
    
    if not DYNAMIC_PROGRESS_ENABLED or not RICH_AVAILABLE:
        return
        
    with PROGRESS_LOCK:
        # Preserve existing counters if requested (for compression phase)
        existing_counters = DYNAMIC_PROGRESS_STATS['counters'].copy() if preserve_stats else {
            'match_found': 0,
            'no_match': 0,
            'skip': 0,
            'override': 0,
            'errors': 0
        }
        
        DYNAMIC_PROGRESS_STATS.update({
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
    if DYNAMIC_PROGRESS_LIVE:
        try:
            DYNAMIC_PROGRESS_LIVE.stop()
        except:
            pass
    
    # Create live display
    if RICH_CONSOLE:
        DYNAMIC_PROGRESS_LIVE = Live(
            _generate_dynamic_progress_display(),
            console=RICH_CONSOLE,
            refresh_per_second=2,  # Reduced to 2 FPS for maximum stability
            transient=False,
            auto_refresh=True
        )
        DYNAMIC_PROGRESS_LIVE.start()


def update_dynamic_progress(file_path: str, result: str = "", log_type: str = "", increment: bool = False):
    """Update the dynamic progress display with throttling to prevent flickering."""
    global DYNAMIC_PROGRESS_STATS, DYNAMIC_PROGRESS_LIVE
    
    if not DYNAMIC_PROGRESS_ENABLED or not DYNAMIC_PROGRESS_LIVE:
        return
    
    current_time = time.time()
    
    with PROGRESS_LOCK:
        # Throttle updates to prevent flickering (except for important updates)
        if not increment and current_time - DYNAMIC_PROGRESS_STATS['last_update_time'] < MIN_UPDATE_INTERVAL:
            return  # Skip this update to prevent flicker
        
        DYNAMIC_PROGRESS_STATS['last_update_time'] = current_time
        # Only increment on actual file completion, not every log message
        if increment:
            DYNAMIC_PROGRESS_STATS['current'] += 1
        
        DYNAMIC_PROGRESS_STATS['current_file'] = os.path.basename(file_path) if file_path else ''
        DYNAMIC_PROGRESS_STATS['last_result'] = result
        
        # Update counters based on log_type or result
        counter_key = None
        if log_type:
            if 'MATCH FOUND' in log_type:
                counter_key = 'match_found'
            elif 'NO MATCH' in log_type:
                counter_key = 'no_match'
            elif 'SKIP' in log_type:
                counter_key = 'skip'
            elif 'OVERRIDE' in log_type:
                counter_key = 'override'
            elif 'ERROR' in log_type or 'FAIL' in log_type:
                counter_key = 'errors'
        elif result:
            if result.lower() == 'skip':
                counter_key = 'skip'
            elif result.lower() == 'loose':
                counter_key = 'override'
            elif result.lower() == 'pack':
                counter_key = 'no_match'
            elif 'fail' in result.lower() or 'error' in result.lower():
                counter_key = 'errors'
            # Don't update counters for compression-related results
            # (copied, extracted, compressing) - these are just status updates
        
        if counter_key:
            DYNAMIC_PROGRESS_STATS['counters'][counter_key] += 1


def update_dynamic_progress_with_counts(file_path: str, result: str = "", log_type: str = "", 
                                       match_found: int = 0, no_match: int = 0, skip: int = 0, 
                                       override: int = 0, errors: int = 0):
    """Update dynamic progress with explicit file counts (prevents chunk counting confusion)."""
    global DYNAMIC_PROGRESS_STATS, DYNAMIC_PROGRESS_LIVE
    
    if not DYNAMIC_PROGRESS_ENABLED or not DYNAMIC_PROGRESS_LIVE:
        return
    
    current_time = time.time()
    
    with PROGRESS_LOCK:
        # Throttle updates to prevent flickering
        if current_time - DYNAMIC_PROGRESS_STATS['last_update_time'] < MIN_UPDATE_INTERVAL:
            return  # Skip this update to prevent flicker
        
        DYNAMIC_PROGRESS_STATS['last_update_time'] = current_time
        DYNAMIC_PROGRESS_STATS['current_file'] = os.path.basename(file_path) if file_path else ''
        DYNAMIC_PROGRESS_STATS['last_result'] = result
        
        # Set explicit counts instead of incrementing (prevents chunk confusion)
        DYNAMIC_PROGRESS_STATS['counters'] = {
            'match_found': match_found,
            'no_match': no_match, 
            'skip': skip,
            'override': override,
            'errors': errors
        }
        
        # Counts updated with explicit values
    
    # Update the live display
    if DYNAMIC_PROGRESS_LIVE:
        try:
            DYNAMIC_PROGRESS_LIVE.update(_generate_dynamic_progress_display())
        except:
            pass  # Ignore display update errors


def finish_dynamic_progress():
    """Finish and close the dynamic progress display."""
    global DYNAMIC_PROGRESS_LIVE, DYNAMIC_PROGRESS_STATS
    
    if not DYNAMIC_PROGRESS_ENABLED:
        return
        
    if DYNAMIC_PROGRESS_LIVE:
        try:
            # Show final state
            DYNAMIC_PROGRESS_LIVE.update(_generate_dynamic_progress_display())
            DYNAMIC_PROGRESS_LIVE.stop()
        except:
            pass
        DYNAMIC_PROGRESS_LIVE = None
    
    # Show final summary
    if RICH_CONSOLE and DYNAMIC_PROGRESS_STATS['total'] > 0:
        with PROGRESS_LOCK:
            elapsed = time.time() - DYNAMIC_PROGRESS_STATS['start_time']
            stats = DYNAMIC_PROGRESS_STATS['counters']
            total = DYNAMIC_PROGRESS_STATS['total']
            stage = DYNAMIC_PROGRESS_STATS['stage']
        
        summary_text = (
            f"✅ [bold bright_green]{stage} COMPLETE![/bold bright_green]\n\n"
            f"📊 [bold bright_white]FINAL STATISTICS:[/bold bright_white]\n"
            f"[bright_cyan]Total Files:[/bright_cyan] {total:,}\n"
            f"[bright_cyan]Processing Time:[/bright_cyan] {elapsed:.1f}s\n"
            f"[bright_green]Matches Found:[/bright_green] {stats['match_found']:,}\n"
            f"[bright_blue]New Files (Pack):[/bright_blue] {stats['no_match']:,}\n"
            f"[bright_yellow]Identical (Skip):[/bright_yellow] {stats['skip']:,}\n"
            f"[bright_magenta]Overrides (Loose):[/bright_magenta] {stats['override']:,}\n"
            f"[red]Errors:[/red] {stats['errors']:,}\n\n"
            f"⚡ [bold bright_white]Average Speed:[/bold bright_white] {total/elapsed:.1f} files/sec"
        )
        
        RICH_CONSOLE.print()
        RICH_CONSOLE.print(Panel(summary_text, title="🎯 Processing Results", style="bright_green"))
        RICH_CONSOLE.print()


def _generate_dynamic_progress_display():
    """Generate the dynamic progress display content."""
    if not DYNAMIC_PROGRESS_ENABLED or not RICH_AVAILABLE:
        return Text("Progress not available")
        
    with PROGRESS_LOCK:
        stats = DYNAMIC_PROGRESS_STATS.copy()  # Thread-safe copy
    
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
    bar_width = 30  # Smaller for compact display
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
        if eta_seconds < 3600:  # Less than 1 hour
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            progress_line.append(f"ETA: {eta_min}m{eta_sec:02d}s", style="dim bright_green")
    
    table.add_row("Progress:", progress_line)
    
    # Current file line
    if stats['current_file']:
        current_file_line = Text()
        current_file_line.append("⚡ ", style="bright_white")
        
        # Clean up and truncate filenames
        filename = stats['current_file']
        
        # Clean up compression-related filenames
        if 'compressing_archive' in filename or filename.endswith('_archive.7z'):
            filename = "Final Archive"
        elif filename.startswith('temp_') or filename.startswith('tmp_'):
            filename = filename[4:]  # Remove temp prefix
        
        # Truncate long filenames
        if len(filename) > 35:
            filename = filename[:32] + "..."
        
        current_file_line.append(filename, style="bright_cyan")
        
        if stats['last_result']:
            if stats['last_result'].lower() == 'skip':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("SKIP", style="bright_yellow")
            elif stats['last_result'].lower() == 'loose':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("LOOSE", style="bright_magenta")
            elif stats['last_result'].lower() == 'pack':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("PACK", style="bright_blue")
            elif stats['last_result'].lower() == 'staging':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("STAGING", style="bright_cyan")
            elif stats['last_result'].lower() == 'path_extracted':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("EXTRACTED", style="bright_green")
            elif stats['last_result'].lower() == 'processing':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("PROCESSING", style="bright_white")
            elif stats['last_result'].lower() == 'compressing':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("COMPRESSING", style="bright_yellow")
            elif stats['last_result'].lower() == 'copied':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("COPIED", style="bright_green")
            elif stats['last_result'].lower() == 'extracted':
                current_file_line.append(" → ", style="dim white")
                current_file_line.append("EXTRACTED", style="bright_cyan")
        
        table.add_row("Current:", current_file_line)
    
    # Stats line
    counters = stats['counters']
    stats_line = Text()
    stats_line.append(f"🎯 {counters['match_found']:,} ", style="bright_green")
    stats_line.append(f"📦 {counters['no_match']:,} ", style="bright_blue")
    stats_line.append(f"⏭️ {counters['skip']:,} ", style="bright_yellow")
    stats_line.append(f"🔄 {counters['override']:,} ", style="bright_magenta")
    if counters['errors'] > 0:
        stats_line.append(f"❌ {counters['errors']:,}", style="red")
    
    table.add_row("Stats:", stats_line)
    
    return table


def handle_dynamic_progress_log(message: str, log_type: str):
    """Handle logging for dynamic progress mode (eliminates spam!)."""
    if not DYNAMIC_PROGRESS_ENABLED:
        return False  # Not handled, let normal logging proceed
        
    # Extract file path and result from log messages
    file_path = ""
    result = ""
    
    # Check for spam messages first (regardless of log_type)
    if 'Copied with Data structure:' in message:
        # File copying messages: "Copied with Data structure: path → target"
        if ' → ' in message:
            file_path = message.split(' → ')[0].replace('Copied with Data structure: ', '')
            file_path = os.path.basename(file_path)
            result = "copied"
        else:
            return True  # Just suppress the message
    elif 'Extracted Data path:' in message:
        # Path extraction messages: "Extracted Data path: path → target"
        if ' → ' in message:
            file_path = message.split(' → ')[0].replace('Extracted Data path: ', '')
            file_path = os.path.basename(file_path)
            result = "extracted"
        else:
            return True  # Just suppress the message
    elif log_type == 'MATCH FOUND' and ' matched to ' in message:
        file_path = message.split(' matched to ')[0].replace('[MATCH FOUND] ', '')
        result = "skip"
    elif log_type == 'NO MATCH' and ' → ' in message:
        parts = message.split(' → ')
        if len(parts) == 2:
            file_path = parts[0].replace('[NO MATCH] ', '')
            result = parts[1].lower()
    elif log_type == 'SKIP' and ' identical' in message:
        file_path = message.replace('[SKIP] ', '').replace(' identical', '')
        result = "skip"
    elif log_type == 'OVERRIDE' and ' differs' in message:
        file_path = message.replace('[OVERRIDE] ', '').replace(' differs', '')
        result = "loose"
    elif 'Classifying' in message:
        file_path = message.replace('Classifying ', '')
        result = "processing"
    elif 'Staged' in message and 'files' in message:
        # Staging progress messages: "Staged 100/500 files..."
        if '/' in message:
            try:
                # Extract current/total from "Staged 100/500 files..."
                parts = message.split()
                for part in parts:
                    if '/' in part:
                        current_total = part.split('/')
                        if len(current_total) == 2:
                            current = int(current_total[0])
                            total = int(current_total[1])
                            file_path = f"staging_progress_{current}_{total}"
                            result = "staging"
                            break
            except (ValueError, IndexError):
                return False
        else:
            return False
    elif log_type == 'PATH_EXTRACT':
        # Path extraction messages: "Found game dir 'meshes': long/path → meshes/relative/path"
        if ' → ' in message:
            parts = message.split(' → ')
            if len(parts) == 2:
                # Extract the original path (before →)
                original_part = parts[0]
                if ':' in original_part:
                    file_path = original_part.split(':')[-1].strip()
                else:
                    file_path = original_part
                result = "path_extracted"
        else:
            return False  # Not a path extraction message we can handle
    elif log_type in ['COPY FAIL', 'LOOSE FAIL', 'HASH FAIL', 'EXCEPTION']:
        # Extract filename from error messages
        if ':' in message:
            file_path = message.split(':')[0].replace(f'[{log_type}] ', '')
        else:
            file_path = message.replace(f'[{log_type}] ', '')[:50]
        result = "error"
    else:
        return False  # Not a classification message, let normal logging handle it
    
    if file_path:
        # Update display but don't increment (classifier handles the counting)
        update_dynamic_progress(file_path, result, log_type, increment=False)
        return True  # Message handled by dynamic progress
    
    return False  # Not handled


def set_dynamic_progress_current(current: int):
    """Manually set the current progress count (for external tracking)."""
    global DYNAMIC_PROGRESS_STATS
    
    if not DYNAMIC_PROGRESS_ENABLED:
        return
        
    with PROGRESS_LOCK:
        DYNAMIC_PROGRESS_STATS['current'] = current


def is_dynamic_progress_enabled() -> bool:
    """Check if dynamic progress mode is enabled."""
    return DYNAMIC_PROGRESS_ENABLED


def simple_progress_fallback(current: int, total: int, stage: str, current_file: str = ""):
    """Simple fallback progress display when Rich is not available."""
    if total == 0:
        return
        
    percent = (current * 100) // total
    bar_width = 30
    filled = int(bar_width * current / total)
    bar = '=' * filled + ' ' * (bar_width - filled)
    
    # Clear line and show progress
    print(f"\r[{bar}] {percent}% | {stage} | {current:,}/{total:,} | {current_file[:30]}", end="", flush=True)
    
    if current >= total:
        print()  # New line when complete
