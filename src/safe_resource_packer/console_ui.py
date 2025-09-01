"""
Console UI - Interactive menu system for non-technical users

Provides a beautiful, user-friendly interface that runs on top of the CLI system.
Users can select options through menus instead of remembering command-line flags.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .utils import log


class ConsoleUI:
    """Interactive console user interface."""

    def __init__(self):
        """Initialize console UI."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

        self.config = {}
        self.mode = None

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the interactive console UI.

        Returns:
            Configuration dictionary for CLI execution, or None to exit
        """
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
                    # Tools & Setup
                    self._tools_menu()
                elif choice == "4":
                    # Help & Info
                    self._help_menu()
                elif choice == "5" or choice.lower() == "q":
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

        print("=" * 60)
        print("🧠 SAFE RESOURCE PACKER - INTERACTIVE MODE")
        print("=" * 60)
        print()
        print("Rich library not available - using basic interface.")
        print("For better experience, install: pip install rich")
        print()

        while True:
            print("MAIN MENU:")
            print("1. Quick Start (Complete Packaging)")
            print("2. Advanced Classification Only")
            print("3. Exit")
            print()

            choice = input("Enter your choice (1-3): ").strip()

            if choice == "1":
                return self._basic_quick_start()
            elif choice == "2":
                return self._basic_classification()
            elif choice == "3":
                print("👋 Thanks for using Safe Resource Packer!")
                return None
            else:
                print("❌ Invalid choice. Please try again.\n")

    def _show_welcome(self):
        """Show welcome screen."""

        welcome_text = Text()
        welcome_text.append("🧠 Safe Resource Packer\n", style="bold blue")
        welcome_text.append("Interactive Console Interface\n\n", style="cyan")
        welcome_text.append("Transform your BodySlide output into professional mod packages!\n", style="white")
        welcome_text.append("No command-line knowledge required. 😊", style="dim")

        welcome_panel = Panel(
            Align.center(welcome_text),
            title="Welcome",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(welcome_panel)
        self.console.print()

    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""

        menu_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
        menu_table.add_column("Option", style="cyan", width=3)
        menu_table.add_column("Description", style="white")
        menu_table.add_column("Details", style="dim")

        menu_table.add_row("1", "🚀 Quick Start", "Complete mod packaging (recommended)")
        menu_table.add_row("2", "🔧 Advanced", "File classification only")
        menu_table.add_row("3", "🛠️  Tools", "Install BSArch, check setup")
        menu_table.add_row("4", "❓ Help", "Philosophy, examples, support")
        menu_table.add_row("5", "🚪 Exit", "Quit the application")

        menu_panel = Panel(
            menu_table,
            title="🎯 What would you like to do?",
            border_style="green"
        )

        self.console.print(menu_panel)

        return Prompt.ask("\n[bold]Enter your choice", choices=["1", "2", "3", "4", "5", "q"], default="1")

    def _quick_start_wizard(self) -> Optional[Dict[str, Any]]:
        """Quick start wizard for complete packaging."""

        self.console.print("\n[bold blue]🚀 QUICK START - COMPLETE MOD PACKAGING[/bold blue]")
        self.console.print("This will create a professional mod package ready for distribution!")
        self.console.print()

        config = {}

        # Step 1: Paths
        self.console.print("[bold]Step 1: File Locations[/bold]")

        config['source'] = self._get_directory_path(
            "📁 Source files directory (e.g., Skyrim Data folder)",
            "This should be your game's Data folder or mod reference files"
        )
        if not config['source']:
            return None

        config['generated'] = self._get_directory_path(
            "📦 Generated files directory (e.g., BodySlide output)",
            "This is where your generated files are located"
        )
        if not config['generated']:
            return None

        config['package'] = self._get_directory_path(
            "🎯 Package output directory",
            "Where to create the final mod package",
            must_exist=False
        )
        if not config['package']:
            return None

        # Step 2: Mod Details
        self.console.print("\n[bold]Step 2: Mod Information[/bold]")

        config['mod_name'] = Prompt.ask(
            "🏷️  Mod name",
            default=os.path.basename(os.path.normpath(config['generated']))
        )

        config['game_type'] = Prompt.ask(
            "🎮 Target game",
            choices=["skyrim", "fallout4"],
            default="skyrim"
        )

        # Step 3: Options
        self.console.print("\n[bold]Step 3: Options[/bold]")

        config['compression'] = IntPrompt.ask(
            "🗜️  Compression level (0=fastest, 9=smallest)",
            default=5,
            choices=range(0, 10)
        )

        config['threads'] = IntPrompt.ask(
            "⚡ Processing threads",
            default=8,
            choices=range(1, 17)
        )

        # ESP Template
        if Confirm.ask("📄 Do you have a custom ESP template?", default=False):
            config['esp_template'] = self._get_file_path(
                "📄 ESP template file path",
                "Path to your custom ESP template file"
            )

        # Advanced options
        if Confirm.ask("🔧 Show advanced options?", default=False):
            config['debug'] = Confirm.ask("🐛 Enable debug mode?", default=False)
            config['no_cleanup'] = Confirm.ask("🗂️  Keep temporary files?", default=False)

        # Summary
        self._show_config_summary(config, "Complete Packaging")

        if Confirm.ask("\n[bold green]🚀 Start packaging?[/bold green]", default=True):
            return self._prepare_packaging_config(config)

        return None

    def _advanced_classification_wizard(self) -> Optional[Dict[str, Any]]:
        """Advanced wizard for classification only."""

        self.console.print("\n[bold blue]🔧 ADVANCED - FILE CLASSIFICATION ONLY[/bold blue]")
        self.console.print("This will classify files without creating packages.")
        self.console.print()

        config = {}

        # Paths
        config['source'] = self._get_directory_path(
            "📁 Source files directory",
            "Reference files for comparison"
        )
        if not config['source']:
            return None

        config['generated'] = self._get_directory_path(
            "📦 Generated files directory",
            "Files to classify"
        )
        if not config['generated']:
            return None

        config['output_pack'] = self._get_directory_path(
            "📦 Pack files output directory",
            "Where to put files safe for archiving",
            must_exist=False
        )
        if not config['output_pack']:
            return None

        config['output_loose'] = self._get_directory_path(
            "📁 Loose files output directory",
            "Where to put files that must stay loose",
            must_exist=False
        )
        if not config['output_loose']:
            return None

        # Options
        config['threads'] = IntPrompt.ask(
            "⚡ Processing threads",
            default=8,
            choices=range(1, 17)
        )

        if Confirm.ask("🔧 Show advanced options?", default=False):
            config['debug'] = Confirm.ask("🐛 Enable debug mode?", default=False)

        # Summary
        self._show_config_summary(config, "File Classification")

        if Confirm.ask("\n[bold green]🚀 Start classification?[/bold green]", default=True):
            return config

        return None

    def _tools_menu(self):
        """Tools and setup menu."""

        while True:
            self.console.print("\n[bold blue]🛠️  TOOLS & SETUP[/bold blue]")

            tools_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
            tools_table.add_column("Option", style="cyan", width=3)
            tools_table.add_column("Description", style="white")

            tools_table.add_row("1", "📦 Install BSArch (optimal BSA/BA2 creation)")
            tools_table.add_row("2", "🔍 Check system setup")
            tools_table.add_row("3", "📋 View ESP templates")
            tools_table.add_row("4", "🔙 Back to main menu")

            self.console.print(Panel(tools_table, title="Tools", border_style="yellow"))

            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"], default="4")

            if choice == "1":
                self._install_bsarch()
            elif choice == "2":
                self._check_system_setup()
            elif choice == "3":
                self._view_esp_templates()
            elif choice == "4":
                break

    def _help_menu(self):
        """Help and information menu."""

        while True:
            self.console.print("\n[bold blue]❓ HELP & INFORMATION[/bold blue]")

            help_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
            help_table.add_column("Option", style="cyan", width=3)
            help_table.add_column("Description", style="white")

            help_table.add_row("1", "🧠 Philosophy - Why this tool exists")
            help_table.add_row("2", "📖 Usage examples")
            help_table.add_row("3", "🎯 Performance benefits")
            help_table.add_row("4", "🔙 Back to main menu")

            self.console.print(Panel(help_table, title="Help", border_style="magenta"))

            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"], default="4")

            if choice == "1":
                self._show_philosophy()
            elif choice == "2":
                self._show_examples()
            elif choice == "3":
                self._show_performance_info()
            elif choice == "4":
                break

    def _get_directory_path(self, prompt: str, description: str, must_exist: bool = True) -> Optional[str]:
        """Get directory path from user with validation."""

        self.console.print(f"\n[cyan]{prompt}[/cyan]")
        if description:
            self.console.print(f"[dim]{description}[/dim]")

        while True:
            path = Prompt.ask("📁 Directory path")

            if not path:
                return None

            path = os.path.expanduser(path)  # Expand ~ to home directory

            if must_exist and not os.path.exists(path):
                self.console.print(f"[red]❌ Directory does not exist: {path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None
                continue

            if must_exist and not os.path.isdir(path):
                self.console.print(f"[red]❌ Path is not a directory: {path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None
                continue

            # Create directory if it doesn't exist and that's okay
            if not must_exist and not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    self.console.print(f"[green]✅ Created directory: {path}[/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ Could not create directory: {e}[/red]")
                    if not Confirm.ask("Try again?", default=True):
                        return None
                    continue

            return path

    def _get_file_path(self, prompt: str, description: str) -> Optional[str]:
        """Get file path from user with validation."""

        self.console.print(f"\n[cyan]{prompt}[/cyan]")
        if description:
            self.console.print(f"[dim]{description}[/dim]")

        while True:
            path = Prompt.ask("📄 File path")

            if not path:
                return None

            path = os.path.expanduser(path)

            if not os.path.exists(path):
                self.console.print(f"[red]❌ File does not exist: {path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None
                continue

            if not os.path.isfile(path):
                self.console.print(f"[red]❌ Path is not a file: {path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None
                continue

            return path

    def _show_config_summary(self, config: Dict[str, Any], mode: str):
        """Show configuration summary."""

        self.console.print(f"\n[bold]📋 {mode} Configuration Summary[/bold]")

        summary_table = Table(show_header=False, box=box.SIMPLE)
        summary_table.add_column("Setting", style="cyan", width=20)
        summary_table.add_column("Value", style="white")

        for key, value in config.items():
            if value is not None:
                display_key = key.replace('_', ' ').title()
                display_value = str(value)

                # Truncate long paths
                if len(display_value) > 50:
                    display_value = "..." + display_value[-47:]

                summary_table.add_row(display_key, display_value)

        self.console.print(summary_table)

    def _prepare_packaging_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare configuration for packaging mode."""

        # Remove None values and add packaging-specific settings
        clean_config = {k: v for k, v in config.items() if v is not None}

        # Set temporary directories for classification
        import tempfile
        temp_base = tempfile.mkdtemp(prefix="srp_console_")
        clean_config['output_pack'] = os.path.join(temp_base, "pack")
        clean_config['output_loose'] = os.path.join(temp_base, "loose")

        return clean_config

    def _install_bsarch(self):
        """Handle BSArch installation."""

        try:
            from .packaging.bsarch_installer import install_bsarch_if_needed

            self.console.print("\n[bold]📦 BSArch Installation[/bold]")
            self.console.print("BSArch creates optimal BSA/BA2 archives for better game performance.")
            self.console.print()

            if install_bsarch_if_needed(interactive=True):
                self.console.print("[green]✅ BSArch installation completed![/green]")
            else:
                self.console.print("[yellow]⚠️  BSArch installation was not completed[/yellow]")

            input("\nPress Enter to continue...")

        except ImportError:
            self.console.print("[red]❌ BSArch installer not available[/red]")
            input("Press Enter to continue...")

    def _check_system_setup(self):
        """Check system setup and requirements."""

        self.console.print("\n[bold]🔍 SYSTEM SETUP CHECK[/bold]")

        check_table = Table(show_header=True, box=box.ROUNDED)
        check_table.add_column("Component", style="cyan")
        check_table.add_column("Status", style="white")
        check_table.add_column("Details", style="dim")

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        python_ok = sys.version_info >= (3, 7)
        python_status = "✅ OK" if python_ok else "❌ Too old"
        check_table.add_row("Python", python_status, f"Version {python_version}")

        # Check Rich
        rich_status = "✅ Available" if RICH_AVAILABLE else "⚠️  Not installed"
        rich_details = "Enhanced UI available" if RICH_AVAILABLE else "Basic UI only"
        check_table.add_row("Rich Library", rich_status, rich_details)

        # Check BSArch
        bsarch_available = False
        try:
            from .packaging.bsarch_installer import BSArchInstaller
            installer = BSArchInstaller()
            bsarch_available = installer.is_bsarch_available()
        except:
            pass

        bsarch_status = "✅ Available" if bsarch_available else "⚠️  Not found"
        bsarch_details = "Optimal BSA/BA2 creation" if bsarch_available else "Will use ZIP fallback"
        check_table.add_row("BSArch", bsarch_status, bsarch_details)

        # Check py7zr
        py7zr_available = False
        try:
            import py7zr
            py7zr_available = True
        except ImportError:
            pass

        py7zr_status = "✅ Available" if py7zr_available else "⚠️  Not found"
        py7zr_details = "7z compression available" if py7zr_available else "Will use ZIP fallback"
        check_table.add_row("py7zr", py7zr_status, py7zr_details)

        self.console.print(check_table)

        # Recommendations
        recommendations = []
        if not RICH_AVAILABLE:
            recommendations.append("💡 Install Rich for better UI: pip install rich")
        if not bsarch_available:
            recommendations.append("💡 Install BSArch for optimal archives: Use option 1 in Tools menu")
        if not py7zr_available:
            recommendations.append("💡 Install py7zr for 7z compression: pip install py7zr")

        if recommendations:
            self.console.print("\n[bold]📝 Recommendations:[/bold]")
            for rec in recommendations:
                self.console.print(rec)
        else:
            self.console.print("\n[green]🎉 All components are available! You're ready to go.[/green]")

        input("\nPress Enter to continue...")

    def _view_esp_templates(self):
        """View available ESP templates."""

        self.console.print("\n[bold]📄 ESP TEMPLATES[/bold]")

        try:
            from .packaging.esp_manager import ESPManager
            esp_manager = ESPManager()
            templates = esp_manager.list_templates()

            if templates:
                template_table = Table(show_header=True, box=box.ROUNDED)
                template_table.add_column("Game", style="cyan")
                template_table.add_column("Template File", style="white")
                template_table.add_column("Status", style="green")

                for game_type, template_path in templates.items():
                    status = "✅ Available" if os.path.exists(template_path) else "❌ Missing"
                    template_table.add_row(
                        game_type.title(),
                        os.path.basename(template_path),
                        status
                    )

                self.console.print(template_table)
            else:
                self.console.print("[yellow]⚠️  No ESP templates found[/yellow]")

        except ImportError:
            self.console.print("[red]❌ ESP manager not available[/red]")

        input("\nPress Enter to continue...")

    def _show_philosophy(self):
        """Show tool philosophy."""

        philosophy_text = """
[bold blue]🧠 Why Safe Resource Packer Exists[/bold blue]

[yellow]THE PROBLEM:[/yellow]
Big modlists create performance nightmares with thousands of loose files.
The Creation Engine treats loose files terribly, causing:

• [red]Slow loading[/red] - 3x longer load times
• [red]Memory waste[/red] - Fragmented memory usage
• [red]Stuttering[/red] - Poor gameplay experience
• [red]Proton pain[/red] - 10x worse on Steam Deck/Linux

[green]OUR SMART SOLUTION:[/green]
Intelligent classification of generated files:

📦 [blue]Pack Files[/blue] - New content safe for BSA/BA2 archives
📁 [magenta]Loose Files[/magenta] - Critical overrides that must stay loose
⏭️ [yellow]Skip Files[/yellow] - Identical copies that waste space

[cyan]THE AMAZING RESULTS:[/cyan]
🚀 [green]3x faster loading times[/green]
🎮 [green]Smooth, stutter-free gameplay[/green]
💾 [green]Optimized memory usage[/green]
🛡️ [green]Zero broken mods or missing assets[/green]
        """

        self.console.print(Panel(philosophy_text, title="Philosophy", border_style="blue"))
        input("\nPress Enter to continue...")

    def _show_examples(self):
        """Show usage examples."""

        examples_text = """
[bold blue]📖 Usage Examples[/bold blue]

[yellow]Scenario 1: BodySlide Output[/yellow]
• Source: Your Skyrim Data folder
• Generated: BodySlide output folder
• Result: Professional mod package ready for Nexus

[yellow]Scenario 2: Texture Overhaul[/yellow]
• Source: Original texture mod
• Generated: Your enhanced textures
• Result: Optimized archive + override files

[yellow]Scenario 3: Multiple Mods[/yellow]
• Source: Combined reference files
• Generated: Merged output from multiple tools
• Result: Single clean package for distribution
        """

        self.console.print(Panel(examples_text, title="Examples", border_style="green"))
        input("\nPress Enter to continue...")

    def _show_performance_info(self):
        """Show performance information."""

        perf_table = Table(title="Performance Comparison", box=box.DOUBLE)
        perf_table.add_column("Method", style="cyan")
        perf_table.add_column("Loading Speed", style="white")
        perf_table.add_column("Memory Usage", style="white")
        perf_table.add_column("Game Performance", style="white")

        perf_table.add_row("BSA/BA2 Archives", "🟢 3x faster", "🟢 Optimal", "🟢 Excellent")
        perf_table.add_row("ZIP Archives", "🟡 2x faster", "🟡 Good", "🟡 Good")
        perf_table.add_row("Loose Files", "🔴 Baseline", "🔴 Poor", "🔴 Poor (stuttering)")

        self.console.print(perf_table)

        benefits_text = """
[bold green]🎯 Key Benefits:[/bold green]

• [green]Faster Loading[/green] - Get into the game 3x quicker
• [green]Smoother Gameplay[/green] - Eliminate stuttering and hitches
• [green]Better Memory Usage[/green] - More efficient RAM utilization
• [green]Cross-Platform[/green] - Especially important for Steam Deck/Linux
• [green]Professional Quality[/green] - Same techniques used by major mods
        """

        self.console.print(Panel(benefits_text, title="Benefits", border_style="green"))
        input("\nPress Enter to continue...")

    def _basic_quick_start(self) -> Optional[Dict[str, Any]]:
        """Basic quick start for when Rich is not available."""

        print("QUICK START - COMPLETE MOD PACKAGING")
        print("-" * 40)

        config = {}

        # Get paths
        config['source'] = input("Source files directory: ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory")
            return None

        config['generated'] = input("Generated files directory: ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory")
            return None

        config['package'] = input("Package output directory: ").strip()
        if not config['package']:
            print("❌ Package directory required")
            return None

        config['mod_name'] = input(f"Mod name [{os.path.basename(config['generated'])}]: ").strip()
        if not config['mod_name']:
            config['mod_name'] = os.path.basename(config['generated'])

        config['game_type'] = input("Game type (skyrim/fallout4) [skyrim]: ").strip().lower()
        if config['game_type'] not in ['skyrim', 'fallout4']:
            config['game_type'] = 'skyrim'

        return self._prepare_packaging_config(config)

    def _basic_classification(self) -> Optional[Dict[str, Any]]:
        """Basic classification for when Rich is not available."""

        print("ADVANCED - FILE CLASSIFICATION ONLY")
        print("-" * 40)

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


def run_console_ui() -> Optional[Dict[str, Any]]:
    """
    Run the console UI and return configuration for CLI execution.

    Returns:
        Configuration dictionary for CLI, or None to exit
    """
    ui = ConsoleUI()
    return ui.run()


if __name__ == "__main__":
    # Test the console UI
    config = run_console_ui()
    if config:
        print("Configuration:", config)
    else:
        print("User cancelled")
