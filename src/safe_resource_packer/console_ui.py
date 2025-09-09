"""
Simplified Console UI - Clean, minimal interactive interface

Provides a simple, user-friendly interface that runs on top of the CLI system.
Users can select options through menus instead of remembering command-line flags.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .dynamic_progress import log
from .batch_repacker import BatchModRepacker


class ConsoleUI:
    """Simplified interactive console user interface."""

    def __init__(self):
        """Initialize console UI."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def run(self) -> Optional[Dict[str, Any]]:
        """Run the interactive console UI."""
        if not RICH_AVAILABLE:
            return self._run_basic_ui()

        try:
            self._show_welcome()

            while True:
                choice = self._show_main_menu()

                if choice == "1":
                    # Quick Start (Packaging)
                    config = self._quick_start_wizard()
                    if config:
                        return config
                elif choice == "2":
                    # Advanced Classification
                    config = self._advanced_classification_wizard()
                    if config:
                        return config
                elif choice == "3":
                    # Batch Mod Repacking
                    config = self._batch_repacking_wizard()
                    if config:
                        return config
                elif choice == "4":
                    # Tools & Setup
                    self._tools_menu()
                elif choice == "5":
                    # Help & Info
                    self._help_menu()
                elif choice == "6" or choice.lower() == "q":
                    # Exit
                    self.console.print("\n[yellow]👋 Thanks for using Safe Resource Packer![/yellow]")
                    return None
                else:
                    self.console.print("[red]❌ Invalid choice. Please try again.[/red]")

        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 Goodbye![/yellow]")
            return None

    def _run_basic_ui(self) -> Optional[Dict[str, Any]]:
        """Fallback text-based UI when Rich is not available."""
        print("\n🧠 Safe Resource Packer - Basic Mode")
        print("=" * 40)
        
        config = {}
        
        config['source'] = input("Source files directory: ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory")
            return None

        config['generated'] = input("Generated files directory: ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory")
            return None

        config['output_pack'] = input("Pack files output directory: ").strip()
        if not config['output_pack']:
            print("❌ Pack output directory required")
            return None

        config['output_loose'] = input("Loose files output directory: ").strip()
        if not config['output_loose']:
            print("❌ Loose output directory required")
            return None

        return config

    def _show_welcome(self):
        """Show welcome message."""
        if not RICH_AVAILABLE:
            return

        welcome_text = """
🧠 [bold blue]Safe Resource Packer[/bold blue] 🧠

[dim]Intelligent mod resource classification and packaging for Bethesda games[/dim]

[bold green]What this tool does:[/bold green]
• Analyzes your mod files and classifies them as "pack" or "loose"
• Creates optimized BSA/BA2 archives for safe-to-pack files
• Keeps override files loose to prevent conflicts
• Perfect for Skyrim, Fallout 4, and other Creation Engine games
        """

        self.console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
        self.console.print()

    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        if not RICH_AVAILABLE:
            print("\n1. Quick Start (Packaging)")
            print("2. Advanced Classification")
            print("3. Batch Mod Repacking")
            print("4. Tools & Setup")
            print("5. Help & Info")
            print("6. Exit")
            return input("Choose an option (1-6): ").strip()

        menu_text = """
[bold cyan]Main Menu[/bold cyan]

[bold green]1.[/bold green] Quick Start (Packaging)
[bold green]2.[/bold green] Advanced Classification
[bold green]3.[/bold green] Batch Mod Repacking  
[bold green]4.[/bold green] Tools & Setup
[bold green]5.[/bold green] Help & Info
[bold green]6.[/bold green] Exit

[dim]Choose an option (1-6):[/dim]
        """

        self.console.print(Panel(menu_text, border_style="cyan"))
        return Prompt.ask("Choice", choices=["1", "2", "3", "4", "5", "6", "q"], default="1")

    def _quick_start_wizard(self) -> Optional[Dict[str, Any]]:
        """Quick start wizard for packaging."""
        if not RICH_AVAILABLE:
            return self._basic_quick_start()

        self.console.print("\n[bold green]🚀 Quick Start - File Packaging[/bold green]")
        self.console.print("[dim]This will classify and package your mod files[/dim]\n")

        # Get source directory
        source = Prompt.ask("Source files directory", default="")
        if not source or not os.path.exists(source):
            self.console.print("[red]❌ Invalid source directory[/red]")
            return None

        # Get generated directory
        generated = Prompt.ask("Generated files directory", default="")
        if not generated or not os.path.exists(generated):
            self.console.print("[red]❌ Invalid generated directory[/red]")
            return None

        # Get output directories
        output_pack = Prompt.ask("Pack files output directory", default="./pack")
        output_loose = Prompt.ask("Loose files output directory", default="./loose")

        # Get optional settings
        threads = Prompt.ask("Number of threads", default="8")
        try:
            threads = int(threads)
        except ValueError:
            threads = 8

        debug = Confirm.ask("Enable debug mode?", default=False)

        config = {
            'source': source,
            'generated': generated,
            'output_pack': output_pack,
            'output_loose': output_loose,
            'threads': threads,
            'debug': debug
        }

        # Show summary
        self.console.print("\n[bold cyan]Configuration Summary:[/bold cyan]")
        self.console.print(f"Source: {source}")
        self.console.print(f"Generated: {generated}")
        self.console.print(f"Pack Output: {output_pack}")
        self.console.print(f"Loose Output: {output_loose}")
        self.console.print(f"Threads: {threads}")
        self.console.print(f"Debug: {debug}")

        if Confirm.ask("\nProceed with this configuration?", default=True):
            return config
        else:
            return None

    def _basic_quick_start(self) -> Optional[Dict[str, Any]]:
        """Basic quick start for when Rich is not available."""
        print("\n🚀 Quick Start - File Packaging")
        print("=" * 40)

        config = {}

        config['source'] = input("Source files directory: ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory")
            return None

        config['generated'] = input("Generated files directory: ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory")
            return None

        config['output_pack'] = input("Pack files output directory: ").strip()
        if not config['output_pack']:
            print("❌ Pack output directory required")
            return None

        config['output_loose'] = input("Loose files output directory: ").strip()
        if not config['output_loose']:
            print("❌ Loose output directory required")
            return None

        return config

    def _batch_repacking_wizard(self) -> Optional[Dict[str, Any]]:
        """Batch repacking wizard."""
        if not RICH_AVAILABLE:
            return self._basic_batch_repacking()

        self.console.print("\n[bold green]📦 Batch Mod Repacking[/bold green]")
        self.console.print("[dim]Repack multiple mods at once[/dim]\n")

        # Get collection directory
        collection = Prompt.ask("Collection directory (contains mod folders)", default="")
        if not collection or not os.path.exists(collection):
            self.console.print("[red]❌ Invalid collection directory[/red]")
            return None

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
        self.console.print("\n[bold cyan]Batch Repacking Configuration:[/bold cyan]")
        self.console.print(f"Collection: {collection}")
        self.console.print(f"Game: {game_type}")
        self.console.print(f"Threads: {threads}")

        if Confirm.ask("\nProceed with batch repacking?", default=True):
            return config
        else:
            return None

    def _basic_batch_repacking(self) -> Optional[Dict[str, Any]]:
        """Basic batch repacking for when Rich is not available."""
        print("\n📦 Batch Mod Repacking")
        print("=" * 30)

        config = {}

        config['collection'] = input("Collection directory: ").strip()
        if not config['collection'] or not os.path.exists(config['collection']):
            print("❌ Invalid collection directory")
            return None

        config['game_type'] = input("Game type (skyrim/fallout4): ").strip().lower()
        if config['game_type'] not in ['skyrim', 'fallout4']:
            config['game_type'] = 'skyrim'

        config['mode'] = 'batch_repacking'
        return config

    def _advanced_classification_wizard(self) -> Optional[Dict[str, Any]]:
        """Advanced classification wizard (classification only)."""
        if not RICH_AVAILABLE:
            return self._basic_classification()

        self.console.print("\n[bold green]🔧 Advanced - File Classification Only[/bold green]")
        self.console.print("[dim]This will only classify files, not create packages[/dim]\n")

        # Get source directory
        source = Prompt.ask("Source files directory", default="")
        if not source or not os.path.exists(source):
            self.console.print("[red]❌ Invalid source directory[/red]")
            return None

        # Get generated directory
        generated = Prompt.ask("Generated files directory", default="")
        if not generated or not os.path.exists(generated):
            self.console.print("[red]❌ Invalid generated directory[/red]")
            return None

        # Get output directories
        output_pack = Prompt.ask("Pack files output directory", default="./pack")
        output_loose = Prompt.ask("Loose files output directory", default="./loose")

        # Get optional settings
        threads = Prompt.ask("Number of threads", default="8")
        try:
            threads = int(threads)
        except ValueError:
            threads = 8

        debug = Confirm.ask("Enable debug mode?", default=False)

        config = {
            'source': source,
            'generated': generated,
            'output_pack': output_pack,
            'output_loose': output_loose,
            'threads': threads,
            'debug': debug,
            'mode': 'classification_only'
        }

        # Show summary
        self.console.print("\n[bold cyan]Classification Configuration:[/bold cyan]")
        self.console.print(f"Source: {source}")
        self.console.print(f"Generated: {generated}")
        self.console.print(f"Pack Output: {output_pack}")
        self.console.print(f"Loose Output: {output_loose}")
        self.console.print(f"Threads: {threads}")
        self.console.print(f"Debug: {debug}")

        if Confirm.ask("\nProceed with classification?", default=True):
            return config
        else:
            return None

    def _basic_classification(self) -> Optional[Dict[str, Any]]:
        """Basic classification for when Rich is not available."""
        print("\n🔧 Advanced - File Classification Only")
        print("=" * 40)

        config = {}

        config['source'] = input("Source files directory: ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory")
            return None

        config['generated'] = input("Generated files directory: ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory")
            return None

        config['output_pack'] = input("Pack files output directory: ").strip()
        if not config['output_pack']:
            print("❌ Pack output directory required")
            return None

        config['output_loose'] = input("Loose files output directory: ").strip()
        if not config['output_loose']:
            print("❌ Loose output directory required")
            return None

        config['mode'] = 'classification_only'
        return config

    def _tools_menu(self):
        """Tools and setup menu."""
        if not RICH_AVAILABLE:
            print("\n🛠️ Tools & Setup")
            print("=" * 20)
            print("1. Install BSArch")
            print("2. Check System Setup")
            print("3. Back to Main Menu")
            choice = input("Choose an option (1-3): ").strip()
            
            if choice == "1":
                self._install_bsarch_basic()
            elif choice == "2":
                self._check_system_basic()
            return

        while True:
            self.console.print("\n[bold green]🛠️ Tools & Setup[/bold green]")
            self.console.print("[dim]System setup and tool installation[/dim]\n")

            tools_text = """
[bold cyan]Available Tools[/bold cyan]

[bold green]1.[/bold green] Install BSArch
[bold green]2.[/bold green] Check System Setup
[bold green]3.[/bold green] Back to Main Menu

[dim]Choose an option (1-3):[/dim]
            """

            self.console.print(Panel(tools_text, border_style="green"))
            choice = Prompt.ask("Choice", choices=["1", "2", "3"], default="1")

            if choice == "1":
                self._install_bsarch()
            elif choice == "2":
                self._check_system()
            elif choice == "3":
                break

    def _install_bsarch(self):
        """Install BSArch for optimal BSA/BA2 creation."""
        if not RICH_AVAILABLE:
            return

        self.console.print("\n[bold blue]📦 BSArch Installation[/bold blue]")
        self.console.print("[dim]Installing BSArch for optimal BSA/BA2 creation...[/dim]\n")

        try:
            from .packaging.bsarch_installer import install_bsarch_if_needed
            success = install_bsarch_if_needed(interactive=True)
            
            if success:
                self.console.print("[green]✅ BSArch installation completed![/green]")
            else:
                self.console.print("[red]❌ BSArch installation failed or was cancelled[/red]")
        except ImportError:
            self.console.print("[red]❌ BSArch installer not available[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")

    def _install_bsarch_basic(self):
        """Basic BSArch installation for when Rich is not available."""
        print("\n📦 BSArch Installation")
        print("=" * 25)
        print("Installing BSArch for optimal BSA/BA2 creation...")
        
        try:
            from .packaging.bsarch_installer import install_bsarch_if_needed
            success = install_bsarch_if_needed(interactive=True)
            
            if success:
                print("✅ BSArch installation completed!")
            else:
                print("❌ BSArch installation failed or was cancelled")
        except ImportError:
            print("❌ BSArch installer not available")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _check_system(self):
        """Check system setup and requirements."""
        if not RICH_AVAILABLE:
            return

        self.console.print("\n[bold blue]🔍 System Setup Check[/bold blue]")
        self.console.print("[dim]Checking system requirements and setup...[/dim]\n")

        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.console.print(f"[green]✅ Python {python_version}[/green]")

        # Check Rich availability
        if RICH_AVAILABLE:
            self.console.print("[green]✅ Rich library available[/green]")
        else:
            self.console.print("[yellow]⚠️ Rich library not available (basic mode)[/yellow]")

        # Check BSArch availability
        try:
            from .packaging.bsarch_installer import BSArchInstaller
            installer = BSArchInstaller()
            if installer.is_bsarch_available():
                self.console.print("[green]✅ BSArch available[/green]")
            else:
                self.console.print("[yellow]⚠️ BSArch not found (will use fallback)[/yellow]")
        except ImportError:
            self.console.print("[yellow]⚠️ BSArch installer not available[/yellow]")

        self.console.print("\n[dim]System check completed![/dim]")

    def _check_system_basic(self):
        """Basic system check for when Rich is not available."""
        print("\n🔍 System Setup Check")
        print("=" * 25)
        print("Checking system requirements and setup...")

        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"✅ Python {python_version}")

        # Check Rich availability
        if RICH_AVAILABLE:
            print("✅ Rich library available")
        else:
            print("⚠️ Rich library not available (basic mode)")

        # Check BSArch availability
        try:
            from .packaging.bsarch_installer import BSArchInstaller
            installer = BSArchInstaller()
            if installer.is_bsarch_available():
                print("✅ BSArch available")
            else:
                print("⚠️ BSArch not found (will use fallback)")
        except ImportError:
            print("⚠️ BSArch installer not available")

        print("\nSystem check completed!")

    def _help_menu(self):
        """Show help and information."""
        if not RICH_AVAILABLE:
            print("\n🧠 Safe Resource Packer - Help")
            print("=" * 30)
            print("This tool helps you classify and package mod files.")
            print("It separates files into 'pack' (safe to archive) and 'loose' (overrides).")
            print("\nFor more information, visit the documentation.")
            return

        help_text = """
[bold blue]Safe Resource Packer - Help[/bold blue]

[bold green]What it does:[/bold green]
• Analyzes mod files and classifies them as "pack" or "loose"
• Creates optimized BSA/BA2 archives for safe-to-pack files
• Keeps override files loose to prevent conflicts

[bold green]Quick Start:[/bold green]
• Choose option 1 for simple file packaging
• Choose option 2 for batch mod repacking

[bold green]For more help:[/bold green]
• Check the documentation
• Use --help flag in command line mode
        """

        self.console.print(Panel(help_text, title="Help", border_style="green"))
        self.console.print()


def run_console_ui() -> Optional[Dict[str, Any]]:
    """Run the console UI and return configuration for CLI execution."""
    ui = ConsoleUI()
    return ui.run()


if __name__ == "__main__":
    # Test the console UI
    config = run_console_ui()
    if config:
        print("Configuration:", config)
    else:
        print("User cancelled")
