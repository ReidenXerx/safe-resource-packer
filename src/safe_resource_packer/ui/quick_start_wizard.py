"""
Quick Start Wizard - Interactive wizard for single mod processing

This module provides the Quick Start wizard functionality for processing individual mods
with an interactive, user-friendly interface.

Naming Conventions:
- Functions with 'quick_start_' prefix: Used for Quick Start mode (single mod processing)
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


class QuickStartWizard:
    """Interactive wizard for Quick Start mode (single mod processing)."""
    
    def __init__(self, console: Console):
        """
        Initialize Quick Start Wizard.
        
        Args:
            console: Rich console instance for output
        """
        self.console = console
    
    def run_wizard(self) -> Optional[Dict[str, Any]]:
        """Run the Quick Start wizard."""
        if not RICH_AVAILABLE:
            return self._basic_quick_start()
        return self._quick_start_wizard()
    
    def _quick_start_wizard(self) -> Optional[Dict[str, Any]]:
        """Rich-enabled Quick Start wizard for packaging."""
        # Check for cached configuration
        from ..config_cache import get_config_cache
        config_cache = get_config_cache()
        cached_config = config_cache.load_config()
        
        # Beautiful header with examples
        header_panel = Panel.fit(
            "[bold bright_green]🚀 Quick Start - File Packaging[/bold bright_green]\n"
            "[dim]Automatically classify and package your mod files[/dim]",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
        
        # Show cached config if available
        if cached_config:
            cache_panel = Panel(
                "[bold green]⚡ Using Last Configuration[/bold green]\n"
                f"[dim]📂 Source: {cached_config.get('source', 'N/A')}\n"
                f"📂 Generated: {cached_config.get('generated', 'N/A')}\n"
                f"📦 Pack Output: {cached_config.get('output_pack', 'N/A')}\n"
                f"📁 Loose Output: {cached_config.get('output_loose', 'N/A')}[/dim]",
                border_style="green",
                padding=(1, 1)
            )
            self.console.print(cache_panel)
            self.console.print()
            
            if not Confirm.ask("Use this configuration?", default=True):
                cached_config = None
        
        if cached_config:
            # Use cached configuration
            config = {
                'source': cached_config.get('source', ''),
                'generated': cached_config.get('generated', ''),
                'output_pack': cached_config.get('output_pack', './pack'),
                'output_loose': cached_config.get('output_loose', './loose'),
                'output_blacklisted': cached_config.get('output_blacklisted', './blacklisted'),
                'threads': cached_config.get('threads', 8),
                'debug': cached_config.get('debug', False),
                'game_type': cached_config.get('game_type', 'skyrim'),
                'compression': cached_config.get('compression', 5)
            }
            
            # Validate that pack and loose directories are different
            if os.path.normpath(os.path.abspath(config['output_pack'])) == os.path.normpath(os.path.abspath(config['output_loose'])):
                self.console.print("[red]❌ Cached configuration has same directory for pack and loose output![/red]")
                self.console.print(f"[red]   Pack: {config['output_pack']}[/red]")
                self.console.print(f"[red]   Loose: {config['output_loose']}[/red]")
                self.console.print("[yellow]⚠️ Please enter new configuration manually[/yellow]")
                cached_config = None
            
            # Show configuration summary
            summary_panel = Panel(
                f"[bold bright_white]📋 Using Cached Configuration[/bold bright_white]\n\n"
                f"[bold green]📂 Source:[/bold green] {config['source']}\n"
                f"[bold green]📂 Generated:[/bold green] {config['generated']}\n"
                f"[bold green]📦 Pack Output:[/bold green] {config['output_pack']}\n"
                f"[bold green]📁 Loose Output:[/bold green] {config['output_loose']}\n"
                f"[bold green]⚡ Threads:[/bold green] {config['threads']}\n"
                f"[bold green]🐛 Debug:[/bold green] {'Yes' if config['debug'] else 'No'}",
                border_style="bright_white",
                padding=(1, 2)
            )
            
            self.console.print(summary_panel)
            self.console.print()
            
            return config
        
        # Show helpful examples
        examples_panel = Panel(
            "[bold yellow]📁 Directory Examples:[/bold yellow]\n"
            "[dim]• Source: C:\\Games\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data\\\n"
            "• Generated: C:\\Games\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data\\Generated\\\n"
            "• Pack Output: ./pack/\n"
            "• Loose Output: ./loose/[/dim]",
            border_style="yellow",
            padding=(1, 1)
        )
        
        self.console.print(examples_panel)
        self.console.print()

        # Get source directory with helpful prompt
        source = Prompt.ask(
            "[bold cyan]📂 Source files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="",
            show_default=False
        )
        
        is_valid, result = self._validate_directory_path(source, "source directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        source = result

        # Get generated directory with helpful prompt
        generated = Prompt.ask(
            "[bold cyan]📂 Generated files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="",
            show_default=False
        )
        
        is_valid, result = self._validate_directory_path(generated, "generated directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        generated = result

        # Get output directories with helpful defaults
        output_pack = Prompt.ask(
            "[bold cyan]📦 Pack files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./pack",
            show_default=True
        )
        output_loose = Prompt.ask(
            "[bold cyan]📁 Loose files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./loose",
            show_default=True
        )
        output_blacklisted = Prompt.ask(
            "[bold cyan]🚫 Blacklisted files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./blacklisted",
            show_default=True
        )
        
        # Validate that directories are different
        directories = [output_pack, output_loose, output_blacklisted]
        for i, dir1 in enumerate(directories):
            for j, dir2 in enumerate(directories[i+1:], i+1):
                if os.path.normpath(os.path.abspath(dir1)) == os.path.normpath(os.path.abspath(dir2)):
                    self.console.print(f"[red]❌ Output directories cannot be the same![/red]")
                    self.console.print(f"[red]   Directory {i+1}: {dir1}[/red]")
                    self.console.print(f"[red]   Directory {j+1}: {dir2}[/red]")
                    return None

        # Get optional settings with helpful hints
        threads = Prompt.ask(
            "[bold cyan]⚡ Number of threads[/bold cyan]",
            default="8",
            show_default=True
        )
        try:
            threads = int(threads)
        except ValueError:
            threads = 8

        debug = Confirm.ask(
            "[bold cyan]🐛 Enable debug mode?[/bold cyan]",
            default=False
        )

        config = {
            'source': source,
            'generated': generated,
            'output_pack': output_pack,
            'output_loose': output_loose,
            'output_blacklisted': output_blacklisted,
            'threads': threads,
            'debug': debug
        }

        # Show beautiful summary
        summary_panel = Panel(
            f"[bold bright_white]📋 Configuration Summary[/bold bright_white]\n\n"
            f"[bold green]📂 Source:[/bold green] {source}\n"
            f"[bold green]📂 Generated:[/bold green] {generated}\n"
            f"[bold green]📦 Pack Output:[/bold green] {output_pack}\n"
            f"[bold green]📁 Loose Output:[/bold green] {output_loose}\n"
            f"[bold green]⚡ Threads:[/bold green] {threads}\n"
            f"[bold green]🐛 Debug:[/bold green] {'Yes' if debug else 'No'}",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(summary_panel)

        if Confirm.ask("\nProceed with this configuration?", default=True):
            return config
        else:
            return None

    def _basic_quick_start(self) -> Optional[Dict[str, Any]]:
        """Basic Quick Start for when Rich is not available."""
        print("\n🚀 Quick Start - File Packaging")
        print("=" * 40)

        config = {}

        config['source'] = input("Source files directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory!")
            return None

        config['generated'] = input("Generated files directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory!")
            return None

        config['output_pack'] = input("Pack files output directory [./pack]: ").strip() or "./pack"
        config['output_loose'] = input("Loose files output directory [./loose]: ").strip() or "./loose"
        config['output_blacklisted'] = input("Blacklisted files output directory [./blacklisted]: ").strip() or "./blacklisted"
        
        # Validate that directories are different
        directories = [config['output_pack'], config['output_loose'], config['output_blacklisted']]
        for i, dir1 in enumerate(directories):
            for j, dir2 in enumerate(directories[i+1:], i+1):
                if os.path.normpath(os.path.abspath(dir1)) == os.path.normpath(os.path.abspath(dir2)):
                    print(f"❌ Output directories cannot be the same!")
                    print(f"   Directory {i+1}: {dir1}")
                    print(f"   Directory {j+1}: {dir2}")
                    return None

        threads_input = input("Number of threads [8]: ").strip()
        try:
            config['threads'] = int(threads_input) if threads_input else 8
        except ValueError:
            config['threads'] = 8

        debug_input = input("Enable debug mode? [n]: ").strip().lower()
        config['debug'] = debug_input in ['y', 'yes', 'true', '1']

        print(f"\n📋 Configuration Summary:")
        print(f"📂 Source: {config['source']}")
        print(f"📂 Generated: {config['generated']}")
        print(f"📦 Pack Output: {config['output_pack']}")
        print(f"📁 Loose Output: {config['output_loose']}")
        print(f"⚡ Threads: {config['threads']}")
        print(f"🐛 Debug: {'Yes' if config['debug'] else 'No'}")

        if input("\nProceed with this configuration? [Y/n]: ").strip().lower() not in ['n', 'no']:
            return config
        else:
            return None

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
