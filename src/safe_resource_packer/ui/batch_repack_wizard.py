"""
Batch Repack Wizard - Interactive wizard for batch mod processing

This module provides the Batch Repack wizard functionality for processing multiple mods
with an interactive, user-friendly interface.

Naming Conventions:
- Functions with 'batch_repack_' prefix: Used for Batch Repacking mode (multiple mods processing)
- Functions without prefix: Shared utilities used by the wizard
"""

import os
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class BatchRepackWizard:
    """Interactive wizard for Batch Repack mode (multiple mods processing)."""
    
    def __init__(self, console: Console):
        """
        Initialize Batch Repack Wizard.
        
        Args:
            console: Rich console instance for output
        """
        self.console = console
    
    def run_wizard(self) -> Optional[Dict[str, Any]]:
        """Run the Batch Repack wizard."""
        if not RICH_AVAILABLE:
            return self._basic_batch_repacking()
        return self._batch_repacking_wizard()
    
    def _batch_repacking_wizard(self) -> Optional[Dict[str, Any]]:
        """Rich-enabled Batch Repacking wizard."""
        # Beautiful header with examples
        header_panel = Panel.fit(
            "[bold bright_green]📦 Batch Mod Repacking[/bold bright_green]\n"
            "[dim]Repack multiple mods at once[/dim]",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
        
        # Show helpful examples
        examples_panel = Panel(
            "[bold yellow]📁 Collection Examples:[/bold yellow]\n"
            "[dim]• Collection: C:\\Games\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data\\\n"
            "• Collection: D:\\ModOrganizer\\mods\\\n"
            "• Collection: C:\\Users\\YourName\\Documents\\My Games\\Skyrim Special Edition\\Mods\\[/dim]",
            border_style="yellow",
            padding=(1, 1)
        )
        
        self.console.print(examples_panel)
        self.console.print()

        # Get collection directory
        collection = Prompt.ask(
            "[bold cyan]📁 Collection directory (contains mod folders)[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default=""
        )
        
        is_valid, result = self._validate_directory_path(collection, "collection directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        collection = result

        # Get game type
        game_type = Prompt.ask("Game type", choices=["skyrim", "fallout4"], default="skyrim")

        # Get threads
        threads = Prompt.ask("Number of threads", default="8")
        try:
            threads = int(threads)
        except ValueError:
            threads = 8

        config = {
            'collection': collection,
            'game_type': game_type,
            'threads': threads,
            'mode': 'batch_repacking'
        }

        # Show summary
        summary_panel = Panel(
            f"[bold bright_white]📋 Batch Repacking Configuration[/bold bright_white]\n\n"
            f"[bold green]📁 Collection:[/bold green] {collection}\n"
            f"[bold green]🎮 Game:[/bold green] {game_type}\n"
            f"[bold green]⚡ Threads:[/bold green] {threads}",
            border_style="bright_white",
            padding=(1, 2)
        )
        
        self.console.print(summary_panel)

        if Confirm.ask("\nProceed with batch repacking?", default=True):
            return config
        else:
            return None

    def _basic_batch_repacking(self) -> Optional[Dict[str, Any]]:
        """Basic Batch Repacking for when Rich is not available."""
        print("\n📦 Batch Mod Repacking")
        print("=" * 30)

        config = {}

        config['collection'] = input("Collection directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['collection'] or not os.path.exists(config['collection']):
            print("❌ Invalid collection directory")
            return None

        config['game_type'] = input("Game type (skyrim/fallout4): ").strip().lower()
        if config['game_type'] not in ['skyrim', 'fallout4']:
            config['game_type'] = 'skyrim'

        config['mode'] = 'batch_repacking'
        return config

    def _validate_directory_path(self, path: str, path_name: str) -> tuple[bool, str]:
        """
        Validate a directory path.
        
        Args:
            path: Path to validate
            path_name: Name of the path for error messages
            
        Returns:
            Tuple of (is_valid, result_path_or_error_message)
        """
        if not path:
            return False, f"{path_name} cannot be empty"
        
        # Handle drag and drop paths (remove quotes if present)
        path = path.strip().strip('"').strip("'")
        
        if not os.path.exists(path):
            return False, f"{path_name} does not exist: {path}"
        
        if not os.path.isdir(path):
            return False, f"{path_name} is not a directory: {path}"
        
        return True, os.path.abspath(path)
