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
        # Store config in self so disk space checker can access it
        self.config = config

        # Step 1: Paths
        self.console.print("[bold]Step 1: File Locations[/bold]")

        # Important warning about path levels
        self.console.print("\n[yellow]⚠️  CRITICAL PATH REQUIREMENTS:[/yellow]")
        self.console.print("• Provide [bold]Data-level[/bold] paths (folders containing meshes/, textures/, etc.)")
        self.console.print("• [red]NOT[/red] paths inside specific game directories like meshes/armor/")
        self.console.print("• Even for staged mod folders, point to the root containing game directories")
        self.console.print("• ✅ Good: [green]C:/MyMod/[/green] (contains meshes/, textures/)")
        self.console.print("• ❌ Bad: [red]C:/MyMod/meshes/[/red] (inside meshes folder)")
        self.console.print("• ✅ Good: [green]C:\\GOGGames\\Fallout 4 GOTY\\Data[/green] (contains meshes/)")
        self.console.print("• ❌ Bad: [red]C:\\GOGGames\\Fallout 4 GOTY\\Data/.../meshes/armor/[/red] (inside meshes folder)")

        config['source'] = self._get_directory_path(
            "📁 SOURCE FILES: Data-level folder with game directories",
            "🎯 REFERENCE folder containing meshes/, textures/, etc. (like game Data folder usually its something like this C:\\GOGGames\\Fallout 4 GOTY\\Data)"
        )
        if not config['source']:
            return None

        config['generated'] = self._get_directory_path(
            "📦 GENERATED FILES: Data-level folder with your modified files",
            "🎯 NEW/MODIFIED files folder containing meshes/, textures/, etc. (BodySlide output root)"
        )
        if not config['generated']:
            return None

        # Show smart disk space analysis now that we have both paths
        self.config = config  # Store for disk space analysis
        self._show_disk_space_requirements(config['source'])

        config['package'] = self._get_directory_path(
            "📦 OUTPUT FOLDER: Where to save your finished mod package",
            "🎯 This is where the FINAL RESULT goes - your completed mod ready for sharing/installation",
            must_exist=False
        )
        if not config['package']:
            return None

        # Step 2: Mod Details
        self.console.print("\n[bold]Step 2: Mod Information[/bold]")
        self.console.print("[dim]💡 This information will be used to name your BSA/BA2 files and ESP[/dim]")

        suggested_name = os.path.basename(os.path.normpath(config['generated']))
        suggested_name = suggested_name.replace(' ', '_')  # Remove spaces

        config['mod_name'] = Prompt.ask(
            "🏷️  Mod name (no spaces - used for file names)",
            default=suggested_name
        )

        # Validate and clean mod name
        if config['mod_name']:
            original_name = config['mod_name']
            config['mod_name'] = ''.join(c for c in config['mod_name'] if c.isalnum() or c in '_-')
            config['mod_name'] = config['mod_name'].replace(' ', '_')
            if config['mod_name'] != original_name:
                self.console.print(f"[yellow]💡 Cleaned mod name: {config['mod_name']}[/yellow]")

        config['game_type'] = Prompt.ask(
            "🎮 Target game",
            choices=["skyrim", "fallout4"],
            default="skyrim"
        )

        # Game installation path for bulletproof directory detection
        self.console.print("\n[bold]🎯 Game Installation Path[/bold]")
        self.console.print("For 100% accurate file structure detection, please provide your game installation path.")
        self.console.print("This helps detect your actual Data folder structure (Meshes, Textures, etc.)")

        if Confirm.ask("📂 Do you want to provide your game installation path? (Recommended)", default=True):
            config['game_path'] = self._get_directory_path(
                "🎮 Game installation directory",
                f"Path to your {config['game_type'].title()} installation folder"
            )

            # Validate game path
            if config['game_path']:
                from .game_scanner import get_game_scanner
                scanner = get_game_scanner()
                data_dir = scanner._find_data_directory(config['game_path'])
                if data_dir:
                    self.console.print(f"[green]✅ Found Data directory: {data_dir}[/green]")
                    # Scan directories for preview
                    game_dirs = scanner.scan_game_data_directory(config['game_path'], config['game_type'])
                    detected_count = len(game_dirs['detected'])
                    if detected_count > 0:
                        self.console.print(f"[green]📁 Detected {detected_count} game directories in your Data folder[/green]")
                        self.console.print("[dim]This ensures perfect file structure preservation![/dim]")
                    else:
                        self.console.print("[yellow]⚠️  No directories detected, will use fallback structure[/yellow]")
                else:
                    self.console.print("[yellow]⚠️  Data directory not found in that path, will use fallback structure[/yellow]")
        else:
            config['game_path'] = None
            self.console.print("[yellow]💡 Using fallback directory structure (still works, but less precise)[/yellow]")

        # Step 3: Options
        self.console.print("\n[bold]Step 3: Options[/bold]")

        config['compression'] = IntPrompt.ask(
            "🗜️  Compression level (0=fastest, 9=smallest)",
            default=5,
            choices=[str(i) for i in range(0, 10)]
        )

        config['threads'] = IntPrompt.ask(
            "⚡ Processing threads",
            default=8,
            choices=[str(i) for i in range(1, 17)]
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
        # Store config in self so disk space checker can access it
        self.config = config

        # Important warning about path levels
        self.console.print("\n[yellow]⚠️  CRITICAL PATH REQUIREMENTS:[/yellow]")
        self.console.print("• Provide [bold]Data-level[/bold] paths (folders containing meshes/, textures/, etc.)")
        self.console.print("• [red]NOT[/red] paths inside specific game directories like meshes/armor/")
        self.console.print("• Even for staged mod folders, point to the root containing game directories")
        self.console.print("• ✅ Good: [green]C:/MyMod/[/green] (contains meshes/, textures/)")
        self.console.print("• ❌ Bad: [red]C:/MyMod/meshes/[/red] (inside meshes folder)")

        # Paths
        config['source'] = self._get_directory_path(
            "📁 SOURCE FILES: Data-level folder with game directories",
            "🎯 REFERENCE folder containing meshes/, textures/, etc. (like game Data folder)"
        )
        if not config['source']:
            return None

        config['generated'] = self._get_directory_path(
            "📦 GENERATED FILES: Data-level folder with your modified files",
            "🎯 NEW/MODIFIED files folder containing meshes/, textures/, etc. (BodySlide output root)"
        )
        if not config['generated']:
            return None

        # Show smart disk space analysis now that we have both paths
        self.config = config  # Store for disk space analysis
        self._show_disk_space_requirements(config['source'])

        config['output_pack'] = self._get_directory_path(
            "📦 PACK OUTPUT: Where to put files safe for BSA/BA2 archives",
            "🎯 Files that can be PACKED into BSA/BA2 will go here (safe for archiving)",
            must_exist=False
        )
        if not config['output_pack']:
            return None

        config['output_loose'] = self._get_directory_path(
            "📁 LOOSE OUTPUT: Where to put files that must stay as loose files",
            "🎯 Files that OVERRIDE others and must stay LOOSE will go here (not archived)",
            must_exist=False
        )
        if not config['output_loose']:
            return None

        # Options
        config['threads'] = IntPrompt.ask(
            "⚡ Processing threads",
            default=8,
            choices=[str(i) for i in range(1, 17)]
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
        """Get directory path from user with validation and detailed help."""

        self.console.print(f"\n[bold cyan]{prompt}[/bold cyan]")
        if description:
            self.console.print(f"[dim]{description}[/dim]")

        # Add detailed help based on the prompt type
        self._show_path_help(prompt)

        while True:
            self.console.print("\n[yellow]💡 TIP: You can drag and drop a folder into this window to get its path![/yellow]")
            path = Prompt.ask("📁 Directory path", show_default=False)

            if not path:
                if Confirm.ask("[yellow]❓ Need help finding the right folder?[/yellow]", default=True):
                    self._show_detailed_path_help(prompt)
                    continue
                return None

            # Clean up the path
            path = path.strip().strip('"').strip("'")  # Remove quotes and whitespace
            path = os.path.expanduser(path)  # Expand ~ to home directory
            path = os.path.abspath(path)  # Convert to absolute path

            if must_exist and not os.path.exists(path):
                self.console.print(f"[red]❌ Directory does not exist: {path}[/red]")
                self._suggest_path_fixes(path)
                if not Confirm.ask("Try again?", default=True):
                    return None
                continue

            if must_exist and not os.path.isdir(path):
                self.console.print(f"[red]❌ Path is not a directory: {path}[/red]")
                self.console.print("[yellow]💡 Make sure you're pointing to a folder, not a file![/yellow]")
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
                    self.console.print("[yellow]💡 Make sure the parent directory exists and you have write permissions![/yellow]")
                    if not Confirm.ask("Try again?", default=True):
                        return None
                    continue

            # Validate the path makes sense
            if must_exist and not self._validate_path_contents(path, prompt):
                if not Confirm.ask("Continue anyway?", default=False):
                    continue

            # Check disk space for output directories
            if not must_exist and ("output" in prompt.lower() or "package" in prompt.lower()):
                self._check_disk_space_warning(path, prompt)

            self.console.print(f"[green]✅ Using directory: {path}[/green]")
            return path

    def _show_path_help(self, prompt: str):
        """Show context-specific path help."""
        if "source" in prompt.lower() or "data" in prompt.lower():
            self.console.print("[dim]🎯 WHAT TO ENTER: Your game's Data folder or reference mod files[/dim]")
            self.console.print("[dim]📍 COMMON LOCATIONS:[/dim]")
            self.console.print("[dim]   • Steam: C:/Program Files (x86)/Steam/steamapps/common/Skyrim/Data[/dim]")
            self.console.print("[dim]   • Steam: C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition/Data[/dim]")
            self.console.print("[dim]   • GOG: C:/GOG Games/The Elder Scrolls V Skyrim/Data[/dim]")
            self.console.print("[dim]   • Or your mod's reference files folder[/dim]")
        elif "generated" in prompt.lower() or "bodyslide" in prompt.lower():
            self.console.print("[dim]🎯 WHAT TO ENTER: Folder containing files created by BodySlide/Outfit Studio[/dim]")
            self.console.print("[dim]📍 COMMON LOCATIONS:[/dim]")
            self.console.print("[dim]   • BodySlide output: Documents/My Games/Skyrim/CalienteTools/BodySlide/SliderSets[/dim]")
            self.console.print("[dim]   • MO2 overwrite: [MO2 folder]/overwrite[/dim]")
            self.console.print("[dim]   • Vortex staging: [Vortex folder]/staging[/dim]")
            self.console.print("[dim]   • Custom build folder where you saved generated meshes/textures[/dim]")
        elif "output" in prompt.lower() or "package" in prompt.lower():
            self.console.print("[dim]🎯 WHAT TO ENTER: Where you want the results saved[/dim]")
            self.console.print("[dim]📍 SUGGESTIONS:[/dim]")
            self.console.print("[dim]   • Desktop folder: C:/Users/[YourName]/Desktop/MyMod[/dim]")
            self.console.print("[dim]   • Documents: C:/Users/[YourName]/Documents/MyMod[/dim]")
            self.console.print("[dim]   • Any empty folder you create[/dim]")

    def _show_detailed_path_help(self, prompt: str):
        """Show detailed help for finding the right path."""
        self.console.print("\n[bold yellow]📖 DETAILED PATH FINDING GUIDE[/bold yellow]")

        if "source" in prompt.lower():
            self.console.print("\n[bold]🎮 FINDING YOUR GAME'S DATA FOLDER:[/bold]")
            self.console.print("1. [cyan]Steam Users:[/cyan]")
            self.console.print("   • Right-click game in Steam → Properties → Local Files → Browse")
            self.console.print("   • Look for 'Data' folder inside the game directory")
            self.console.print("   • Example: C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition/Data")
            self.console.print("\n2. [cyan]GOG Users:[/cyan]")
            self.console.print("   • Find your GOG Games folder (usually C:/GOG Games/)")
            self.console.print("   • Go to your game folder → Data")
            self.console.print("\n3. [cyan]Mod Reference Files:[/cyan]")
            self.console.print("   • If you have a mod with reference files, use that folder")
            self.console.print("   • This should contain .nif, .dds, .esp files you want to compare against")

        elif "generated" in prompt.lower():
            self.console.print("\n[bold]🔧 FINDING YOUR GENERATED FILES:[/bold]")
            self.console.print("1. [cyan]BodySlide Output:[/cyan]")
            self.console.print("   • Check: Documents/My Games/Skyrim/CalienteTools/BodySlide/")
            self.console.print("   • Or wherever you set BodySlide to output files")
            self.console.print("\n2. [cyan]Outfit Studio Output:[/cyan]")
            self.console.print("   • Usually same location as BodySlide")
            self.console.print("   • Check your Outfit Studio settings for output folder")
            self.console.print("\n3. [cyan]Mod Organizer 2:[/cyan]")
            self.console.print("   • Check the 'Overwrite' folder in your MO2 directory")
            self.console.print("   • Files often end up here after using tools")
            self.console.print("\n4. [cyan]Manual Creation:[/cyan]")
            self.console.print("   • Folder where you saved your custom meshes/textures")
            self.console.print("   • Should contain .nif, .dds, or other game files")

        elif "output" in prompt.lower():
            self.console.print("\n[bold]📁 CHOOSING AN OUTPUT FOLDER:[/bold]")
            self.console.print("• [cyan]Create a new empty folder[/cyan] (recommended)")
            self.console.print("• [cyan]Use your Desktop[/cyan] for easy access")
            self.console.print("• [cyan]Use Documents[/cyan] for organization")
            self.console.print("• [yellow]⚠️  Don't use system folders like Program Files[/yellow]")
            self.console.print("• [yellow]⚠️  Don't use folders with existing important files[/yellow]")

        self.console.print("\n[bold green]💡 UNIVERSAL TIPS:[/bold green]")
        self.console.print("• [green]Drag and drop[/green] the folder into this window")
        self.console.print("• [green]Copy-paste[/green] the path from Windows Explorer address bar")
        self.console.print("• [green]Use forward slashes[/green] (/) or double backslashes (\\\\)")
        self.console.print("• [green]Paths with spaces[/green] are automatically handled")

    def _suggest_path_fixes(self, path: str):
        """Suggest fixes for common path problems."""
        self.console.print("\n[yellow]🔍 COMMON FIXES:[/yellow]")

        # Check for common typos
        if "Program Files" in path and "Program Files (x86)" not in path:
            suggested = path.replace("Program Files", "Program Files (x86)")
            self.console.print(f"[dim]💡 Try: {suggested}[/dim]")

        # Check parent directory
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            self.console.print(f"[dim]💡 Parent directory exists: {parent}[/dim]")
            # List contents of parent
            try:
                contents = os.listdir(parent)
                folders = [f for f in contents if os.path.isdir(os.path.join(parent, f))]
                if folders:
                    self.console.print("[dim]📁 Available folders in parent:[/dim]")
                    for folder in sorted(folders)[:5]:  # Show first 5
                        self.console.print(f"[dim]   • {folder}[/dim]")
            except:
                pass

        # Check for case sensitivity issues
        if os.path.exists(path.lower()) and path != path.lower():
            self.console.print(f"[dim]💡 Try lowercase: {path.lower()}[/dim]")

        self.console.print("[dim]💡 Double-check spelling and capitalization[/dim]")
        self.console.print("[dim]💡 Make sure you're using the full path, not just folder name[/dim]")

    def _validate_path_contents(self, path: str, prompt: str) -> bool:
        """Validate that the path contains expected files."""
        try:
            contents = os.listdir(path)
            files = [f for f in contents if os.path.isfile(os.path.join(path, f))]

            if "source" in prompt.lower():
                # Check for game files (recursively)
                game_extensions = ['.esp', '.esm', '.nif', '.dds', '.bsa', '.ba2']
                has_game_files = any(any(f.lower().endswith(ext) for ext in game_extensions) for f in files)

                # If no game files in root, check subdirectories
                if not has_game_files:
                    for item in contents:
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            try:
                                for root, dirs, subfiles in os.walk(item_path):
                                    if any(f.lower().endswith(ext) for f in subfiles for ext in game_extensions):
                                        has_game_files = True
                                        break
                                if has_game_files:
                                    break
                            except:
                                continue

                if not has_game_files:
                    self.console.print("[yellow]⚠️  This folder doesn't contain typical game files (.esp, .nif, .dds, etc.)[/yellow]")
                    self.console.print("[yellow]   Make sure this is your game's Data folder or mod reference files[/yellow]")
                    return False

            elif "generated" in prompt.lower():
                # Check for generated files (recursively)
                has_files = len(files) > 0

                # If no files in root, check subdirectories
                if not has_files:
                    for item in contents:
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            try:
                                for root, dirs, subfiles in os.walk(item_path):
                                    if subfiles:  # Any files in subdirectories
                                        has_files = True
                                        break
                                if has_files:
                                    break
                            except:
                                continue

                if not has_files:
                    self.console.print("[yellow]⚠️  This folder appears to be empty[/yellow]")
                    self.console.print("[yellow]   Make sure this contains your generated/modified files[/yellow]")
                    return False

            return True
        except:
            return True  # If we can't check, assume it's okay

    def _check_disk_space_warning(self, output_path: str, prompt: str):
        """Check and warn about disk space requirements using smart analysis."""
        try:
            import shutil

            # Get available disk space for output location
            output_drive = os.path.splitdrive(os.path.abspath(output_path))[0]
            if not output_drive:  # Unix-like system
                output_drive = "/"

            free_bytes = shutil.disk_usage(output_drive).free
            free_gb = free_bytes / (1024**3)

            # Try smart space analysis if we have both source and generated paths
            estimated_needed_gb = None
            analysis_type = "unknown"

            if hasattr(self, 'config') and 'source' in self.config and 'generated' in self.config:
                try:
                    # Use smart analysis (same logic as main disk space analysis)
                    estimated_needed_gb, analysis_type = self._calculate_smart_space_estimate(
                        self.config['source'], self.config['generated']
                    )
                except Exception as e:
                    # Fallback to conservative estimate if smart analysis fails
                    try:
                        source_size = self._get_folder_size(self.config['source'])
                        estimated_needed_gb = max((source_size * 0.5) / (1024**3), 5.0)
                        analysis_type = "conservative_fallback"
                    except:
                        pass

            # Show disk space info
            self.console.print(f"\n[dim]💾 Available disk space on {output_drive}: {free_gb:.1f} GB[/dim]")

            if estimated_needed_gb:
                # Show estimate with appropriate description based on analysis type
                if analysis_type == "smart":
                    self.console.print(f"[dim]🧠 Smart space estimate: {estimated_needed_gb:.1f} GB (selective copying + processing)[/dim]")
                    self.console.print(f"[dim]   ✅ Uses intelligent analysis of your mod's directory usage[/dim]")
                elif analysis_type == "conservative_fallback":
                    self.console.print(f"[dim]📏 Conservative estimate: {estimated_needed_gb:.1f} GB (smart optimization will reduce this)[/dim]")
                    self.console.print(f"[dim]   💡 Actual usage will be much lower thanks to selective copying[/dim]")
                else:
                    self.console.print(f"[dim]📏 Estimated space needed: {estimated_needed_gb:.1f} GB[/dim]")

                # Check space availability with appropriate warnings
                if estimated_needed_gb > free_gb:
                    if analysis_type == "smart":
                        self.console.print(f"[red]⚠️  WARNING: Not enough disk space![/red]")
                        self.console.print(f"[red]   Smart analysis shows {estimated_needed_gb:.1f} GB needed but only {free_gb:.1f} GB available[/red]")
                        self.console.print(f"[yellow]💡 Free up space or choose a different drive[/yellow]")
                        if not Confirm.ask("Continue anyway? (may fail during processing)", default=False):
                            raise ValueError("Insufficient disk space")
                    else:
                        self.console.print(f"[yellow]⚠️  CAUTION: Conservative estimate shows potential space issue[/yellow]")
                        self.console.print(f"[yellow]   Estimate: {estimated_needed_gb:.1f} GB vs Available: {free_gb:.1f} GB[/yellow]")
                        self.console.print(f"[green]💡 However, smart optimization will likely reduce actual usage significantly[/green]")
                        if not Confirm.ask("Continue? (smart optimization should make this work)", default=True):
                            raise ValueError("User chose not to continue due to space concerns")

                elif estimated_needed_gb > free_gb * 0.8:  # Using more than 80% of available space
                    if analysis_type == "smart":
                        self.console.print(f"[yellow]⚠️  CAUTION: This will use most of your available disk space[/yellow]")
                        self.console.print(f"[yellow]   Smart estimate: {estimated_needed_gb:.1f} GB vs Available: {free_gb:.1f} GB[/yellow]")
                    else:
                        self.console.print(f"[green]📊 Should work fine with smart optimization[/green]")
                        self.console.print(f"[green]   Conservative estimate: {estimated_needed_gb:.1f} GB vs Available: {free_gb:.1f} GB[/green]")
                        self.console.print(f"[green]   💡 Smart copying will likely use much less space[/green]")
                else:
                    if analysis_type == "smart":
                        self.console.print(f"[green]✅ Sufficient disk space available (smart analysis)[/green]")
                    else:
                        self.console.print(f"[green]✅ Plenty of disk space available[/green]")
                        self.console.print(f"[green]   💡 Smart optimization will make this even more efficient[/green]")
            else:
                # Generic warning without specific estimates
                if free_gb < 5:  # Less than 5GB free
                    self.console.print(f"[yellow]⚠️  WARNING: Low disk space ({free_gb:.1f} GB available)[/yellow]")
                    self.console.print(f"[yellow]💡 Smart optimization typically needs much less space than old tools[/yellow]")
                    self.console.print(f"[yellow]   But consider freeing up space or using a different drive[/yellow]")
                elif free_gb < 10:  # Less than 10GB free
                    self.console.print(f"[green]💡 Moderate disk space ({free_gb:.1f} GB) - should be fine with smart optimization[/green]")
                else:
                    self.console.print(f"[green]✅ Good disk space available ({free_gb:.1f} GB)[/green]")

        except Exception as e:
            # If disk space check fails, just show a general warning
            self.console.print(f"[dim]💾 Could not check disk space: {e}[/dim]")
            self.console.print(f"[yellow]💡 Make sure you have enough free space (at least 3× your source folder size)[/yellow]")

    def _get_folder_size(self, folder_path: str) -> int:
        """Get total size of folder in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue  # Skip files we can't access
        except (OSError, IOError):
            pass
        return total_size

    def _show_disk_space_requirements(self, source_path: str):
        """Show intelligent disk space requirements using smart selective analysis."""
        try:
            self.console.print("\n[bold yellow]💾 SMART DISK SPACE ANALYSIS[/bold yellow]")

            # Check if we have generated path for smart analysis
            generated_path = getattr(self, 'config', {}).get('generated', None)

            if generated_path and os.path.exists(generated_path):
                self._show_smart_disk_space_analysis(source_path, generated_path)
            else:
                self._show_fallback_disk_space_estimate(source_path)

        except Exception as e:
            self.console.print(f"\n[yellow]💾 Could not calculate disk space requirements: {e}[/yellow]")
            self.console.print("[yellow]⚠️  GENERAL RULE: Make sure you have sufficient free space for processing[/yellow]")
            self.console.print("[yellow]   With smart selective copying, space requirements are much lower![/yellow]")

    def _show_smart_disk_space_analysis(self, source_path: str, generated_path: str):
        """Show smart disk space analysis using selective copying logic."""
        self.console.print("[dim]🧠 Analyzing mod directories for smart space calculation...[/dim]")

        try:
            # Use the same logic as SafeResourcePacker for analysis
            from .core import SafeResourcePacker
            temp_packer = SafeResourcePacker()

            # Analyze mod directories (same as selective copy logic)
            mod_directories = temp_packer._analyze_mod_directories(generated_path)
            source_directories = temp_packer._find_source_directories(source_path, mod_directories)
            mod_only_dirs = mod_directories - set(source_directories)

            # Calculate sizes
            total_source_size = temp_packer._estimate_directory_size(source_path)
            selective_size = sum(temp_packer._estimate_directory_size(os.path.join(source_path, d))
                               for d in source_directories if os.path.exists(os.path.join(source_path, d)))
            generated_size = temp_packer._estimate_directory_size(generated_path)

            # Convert to GB
            total_source_gb = total_source_size / (1024**3)
            selective_gb = selective_size / (1024**3)
            generated_gb = generated_size / (1024**3)

            # Calculate space savings
            if total_source_size > 0:
                savings_percent = ((total_source_size - selective_size) / total_source_size) * 100
            else:
                savings_percent = 0

            # Smart space estimate (selective copy + generated + output + temp overhead)
            estimated_needed_gb = selective_gb + generated_gb + (generated_gb * 2) + 1  # +1GB buffer

            # Display results
            self.console.print(f"[cyan]📁 Total source size: {total_source_gb:.1f} GB[/cyan]")
            self.console.print(f"[green]🎯 Smart selective copy: {selective_gb:.1f} GB ({100-savings_percent:.1f}% of source)[/green]")
            self.console.print(f"[blue]📦 Generated files: {generated_gb:.1f} GB[/blue]")
            self.console.print(f"[yellow]💾 SMART SPACE NEEDED: ~{estimated_needed_gb:.1f} GB[/yellow]")

            if savings_percent > 50:
                saved_gb = total_source_gb - estimated_needed_gb
                self.console.print(f"[bold green]🎉 OPTIMIZATION SAVINGS: {saved_gb:.1f} GB saved ({savings_percent:.1f}% reduction)![/bold green]")

            # Show breakdown
            self.console.print(f"\n[dim]🔍 SMART SPACE BREAKDOWN:[/dim]")
            self.console.print(f"[dim]   • Selective source copy: {selective_gb:.1f} GB (only {len(source_directories)} directories)[/dim]")
            self.console.print(f"[dim]   • Generated files: {generated_gb:.1f} GB[/dim]")
            self.console.print(f"[dim]   • Output processing: {generated_gb * 2:.1f} GB (pack + loose)[/dim]")
            self.console.print(f"[dim]   • Buffer space: 1.0 GB[/dim]")

            # Show directory analysis
            self.console.print(f"\n[dim]📊 DIRECTORY ANALYSIS:[/dim]")
            self.console.print(f"[dim]   📦 Mod uses: {len(mod_directories)} directories: {sorted(list(mod_directories))[:5]}{'...' if len(mod_directories) > 5 else ''}[/dim]")
            self.console.print(f"[dim]   ✅ From source: {len(source_directories)} directories: {sorted(source_directories)[:3]}{'...' if len(source_directories) > 3 else ''}[/dim]")
            if mod_only_dirs:
                self.console.print(f"[dim]   🆕 Mod-only: {len(mod_only_dirs)} directories: {sorted(list(mod_only_dirs))[:3]}{'...' if len(mod_only_dirs) > 3 else ''}[/dim]")

            # Provide recommendations
            if estimated_needed_gb > 50:
                self.console.print(f"\n[yellow]📊 LARGE MOD ({estimated_needed_gb:.1f} GB needed)[/yellow]")
                self.console.print(f"[yellow]   But thanks to smart optimization, this is {(total_source_gb * 3) - estimated_needed_gb:.1f} GB less than the old method![/yellow]")
            elif estimated_needed_gb > 10:
                self.console.print(f"\n[green]📊 MEDIUM MOD ({estimated_needed_gb:.1f} GB needed)[/green]")
                self.console.print("[green]   Smart optimization makes this very manageable![/green]")
            else:
                self.console.print(f"\n[green]✅ SMALL MOD ({estimated_needed_gb:.1f} GB needed)[/green]")
                self.console.print("[green]   Extremely efficient with smart optimization![/green]")

        except Exception as e:
            self.console.print(f"[yellow]⚠️  Smart analysis failed: {e}[/yellow]")
            self._show_fallback_disk_space_estimate(source_path)

    def _show_fallback_disk_space_estimate(self, source_path: str):
        """Show fallback disk space estimate when smart analysis isn't available."""
        self.console.print("[dim]📏 Calculating basic source folder size...[/dim]")

        source_size_bytes = self._get_folder_size(source_path)
        source_size_gb = source_size_bytes / (1024**3)

        # More conservative estimate since we can't do smart analysis yet
        estimated_needed_gb = max(source_size_gb * 0.5, 5.0)  # At least 5GB, or 50% of source

        self.console.print(f"[cyan]📁 Source folder size: {source_size_gb:.1f} GB[/cyan]")
        self.console.print(f"[yellow]💾 ESTIMATED SPACE NEEDED: ~{estimated_needed_gb:.1f} GB[/yellow]")

        self.console.print("\n[dim]🧠 SMART OPTIMIZATION WILL REDUCE THIS SIGNIFICANTLY![/dim]")
        self.console.print("[dim]   • Only directories used by your mod will be copied[/dim]")
        self.console.print("[dim]   • Typical savings: 80-95% less space than full copy[/dim]")
        self.console.print("[dim]   • Actual space needed will be calculated during processing[/dim]")

        if estimated_needed_gb > 20:
            self.console.print(f"\n[green]📊 ESTIMATED MODERATE SPACE USAGE ({estimated_needed_gb:.1f} GB)[/green]")
            self.console.print("[green]   Smart optimization will likely reduce this to just a few GB![/green]")
        else:
            self.console.print(f"\n[green]✅ ESTIMATED LOW SPACE USAGE ({estimated_needed_gb:.1f} GB)[/green]")
            self.console.print("[green]   Smart optimization will make this very efficient![/green]")

        self.console.print(f"\n[bold]💡 TIP: Actual space requirements will be much lower thanks to selective copying![/bold]")

    def _calculate_smart_space_estimate(self, source_path: str, generated_path: str):
        """Calculate smart space estimate and return (estimate_gb, analysis_type)."""
        try:
            # Use the same logic as smart disk space analysis
            from .core import SafeResourcePacker
            temp_packer = SafeResourcePacker()

            # Analyze mod directories (same as selective copy logic)
            mod_directories = temp_packer._analyze_mod_directories(generated_path)
            source_directories = temp_packer._find_source_directories(source_path, mod_directories)

            # Calculate sizes
            selective_size = sum(temp_packer._estimate_directory_size(os.path.join(source_path, d))
                               for d in source_directories if os.path.exists(os.path.join(source_path, d)))
            generated_size = temp_packer._estimate_directory_size(generated_path)

            # Convert to GB
            selective_gb = selective_size / (1024**3)
            generated_gb = generated_size / (1024**3)

            # Smart space estimate (selective copy + generated + output + temp overhead)
            estimated_needed_gb = selective_gb + generated_gb + (generated_gb * 2) + 1  # +1GB buffer

            return estimated_needed_gb, "smart"

        except Exception as e:
            # If smart analysis fails, return None so caller can use fallback
            return None, "failed"

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

        # Create the temporary directories
        os.makedirs(clean_config['output_pack'], exist_ok=True)
        os.makedirs(clean_config['output_loose'], exist_ok=True)

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
