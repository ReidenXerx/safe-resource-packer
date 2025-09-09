"""
Clean and beautiful live output system for Safe Resource Packer.
"""

import sys
import time
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class CleanOutputManager:
    """Manages clean, beautiful live output during processing."""
    
    def __init__(self, console: Optional[Console] = None, quiet: bool = False):
        """
        Initialize the clean output manager.
        
        Args:
            console: Rich console instance
            quiet: Enable quiet mode (minimal output)
        """
        self.console = console or Console() if RICH_AVAILABLE else None
        self.quiet = quiet
        self.stats = {
            'pack': 0,
            'loose': 0, 
            'skip': 0,
            'error': 0,
            'current_file': '',
            'total_files': 0,
            'processed': 0,
            'start_time': time.time()
        }
        self.live = None
        self.progress_task = None
        
    def start_processing(self, total_files: int):
        """Start the processing display."""
        self.stats['total_files'] = total_files
        self.stats['start_time'] = time.time()
        
        if not RICH_AVAILABLE or self.quiet:
            if not self.quiet:
                print(f"🔄 Processing {total_files} files...")
            return
        
        # Create the live display
        self.live = Live(
            self._create_display(),
            refresh_per_second=4,
            console=self.console
        )
        self.live.start()
    
    def update_progress(self, current_file: str, result_type: str):
        """
        Update progress with current file and result.
        
        Args:
            current_file: Name of current file being processed
            result_type: Type of result ('pack', 'loose', 'skip', 'error')
        """
        self.stats['processed'] += 1
        self.stats['current_file'] = current_file
        
        if result_type in self.stats:
            self.stats[result_type] += 1
        
        if not RICH_AVAILABLE or self.quiet:
            if not self.quiet:
                # Simple progress for non-rich mode
                percent = (self.stats['processed'] / self.stats['total_files']) * 100
                status_icon = {
                    'pack': '📦',
                    'loose': '📁', 
                    'skip': '⏭️',
                    'error': '❌'
                }.get(result_type, '🔄')
                
                print(f"\r{status_icon} [{percent:5.1f}%] {current_file[:50]:<50}", end='', flush=True)
            return
        
        # Update rich display
        if self.live:
            self.live.update(self._create_display())
    
    def finish_processing(self):
        """Finish the processing display."""
        if self.live:
            self.live.stop()
            self.live = None
        elif not self.quiet:
            print()  # New line after progress
    
    def _create_display(self) -> Panel:
        """Create the rich display panel."""
        if not RICH_AVAILABLE:
            return None
        
        # Calculate progress
        progress_percent = (self.stats['processed'] / max(self.stats['total_files'], 1)) * 100
        elapsed_time = time.time() - self.stats['start_time']
        
        # Estimate remaining time
        if self.stats['processed'] > 0:
            rate = self.stats['processed'] / elapsed_time
            remaining = max(0, (self.stats['total_files'] - self.stats['processed']) / rate)
            eta_text = f"{remaining:.0f}s remaining"
        else:
            eta_text = "Calculating..."
        
        # Create progress bar
        progress_bar = "█" * int(progress_percent / 2.5) + "░" * (40 - int(progress_percent / 2.5))
        
        # Create stats table
        stats_table = Table.grid(padding=1)
        stats_table.add_column(style="cyan", no_wrap=True)
        stats_table.add_column(style="white", no_wrap=True)
        stats_table.add_column(style="yellow", justify="right")
        
        stats_table.add_row("📦 Pack", "New files safe to pack", str(self.stats['pack']))
        stats_table.add_row("📁 Loose", "Override files (keep loose)", str(self.stats['loose']))
        stats_table.add_row("⏭️ Skip", "Identical files", str(self.stats['skip']))
        if self.stats['error'] > 0:
            stats_table.add_row("❌ Error", "Processing errors", str(self.stats['error']))
        
        # Current file display (truncated)
        current_file_display = self.stats['current_file']
        if len(current_file_display) > 60:
            current_file_display = "..." + current_file_display[-57:]
        
        # Create the main content
        content = f"""[bold blue]Processing Files[/bold blue]

[green]{progress_bar}[/green] [yellow]{progress_percent:.1f}%[/yellow]
[dim]{self.stats['processed']}/{self.stats['total_files']} files • {eta_text}[/dim]

[bold]Current:[/bold] [cyan]{current_file_display}[/cyan]

[bold]Statistics:[/bold]
{stats_table}

[dim]Elapsed: {elapsed_time:.1f}s • Rate: {self.stats['processed']/max(elapsed_time, 0.1):.1f} files/s[/dim]"""
        
        return Panel(
            content,
            title="🧠 Safe Resource Packer",
            border_style="blue",
            padding=(1, 2)
        )


class SimpleProgressCallback:
    """Simple progress callback for basic mode."""
    
    def __init__(self, quiet: bool = False):
        """Initialize simple progress callback."""
        self.quiet = quiet
        self.last_update = 0
        self.update_interval = 0.1  # Update every 100ms
    
    def __call__(self, current: int, total: int, stage: str, extra: str = ""):
        """Progress callback function."""
        if self.quiet:
            return
        
        current_time = time.time()
        if current_time - self.last_update < self.update_interval and current < total:
            return
        
        self.last_update = current_time
        
        # Determine status icon based on the file type or result
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
        sys.stdout.write(f"\r{icon} [{bar}] {percent:5.1f}% {filename:<40}")
        sys.stdout.flush()
        
        if current >= total:
            print()  # New line when complete


def create_clean_progress_callback(console: Optional[Console] = None, quiet: bool = False):
    """
    Create a clean progress callback for the classifier.
    
    Args:
        console: Rich console instance
        quiet: Enable quiet mode
        
    Returns:
        Progress callback function or CleanOutputManager
    """
    if RICH_AVAILABLE and not quiet and console:
        # Return a rich-based output manager
        manager = CleanOutputManager(console, quiet)
        return manager
    else:
        # Return simple callback
        return SimpleProgressCallback(quiet)


def enhance_classifier_output(classifier, quiet: bool = False):
    """
    Enhance classifier output to be cleaner and prettier.
    
    Args:
        classifier: PathClassifier instance
        quiet: Enable quiet mode
    """
    # Store original process_file method
    original_process_file = classifier.process_file
    
    def clean_process_file(*args, **kwargs):
        """Wrapper for process_file with cleaner output."""
        result, path = original_process_file(*args, **kwargs)
        
        # Only log significant events, not every file
        if not quiet and result in ['loose', 'error']:
            # Only show important events
            if result == 'loose':
                print(f"📁 Override: {Path(path).name}")
            elif result == 'error':
                print(f"❌ Error: {Path(path).name}")
        
        return result, path
    
    # Replace the method
    classifier.process_file = clean_process_file
    return classifier
