"""
Simplified Console UI - Clean, minimal interactive interface

Provides a simple, user-friendly interface that runs on top of the CLI system.
Users can select options through menus instead of remembering command-line flags.

Naming Conventions:
- Functions with 'quick_start_' prefix: Used for Intelligent Packer mode (single mod processing)
- Functions with 'batch_repack_' prefix: Used for Batch Repacking mode (multiple mods processing)
- Functions without prefix: Shared UI utilities used by both modes
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import the new UI components
from .ui import QuickStartWizard, BatchRepackWizard, UIUtilities

# Import the new noob-friendly components
from .onboarding import FirstTimeDetector, UserProfiler, AdaptiveWelcome
from .guides import DataPreparationGuide, ResultsGuide, TroubleshootingGuide  
from .tutorials import InteractiveTutorial, ExampleDataGenerator, ComprehensionChecker


class ConsoleUI:
    """Simplified Console UI using modular components."""

    def __init__(self):
        """Initialize Console UI."""
        self.console = Console() if RICH_AVAILABLE else None

        # Initialize UI components
        self.ui_utils = UIUtilities(self.console) if RICH_AVAILABLE else None
        self.quick_start_wizard = QuickStartWizard(self.console) if RICH_AVAILABLE else None
        self.batch_repack_wizard = BatchRepackWizard(self.console) if RICH_AVAILABLE else None
        
        # Initialize noob-friendly components
        self.first_time_detector = FirstTimeDetector()
        self.user_profiler = UserProfiler()
        self.adaptive_welcome = AdaptiveWelcome(self.console)
        self.data_prep_guide = DataPreparationGuide(self.console)
        self.results_guide = ResultsGuide(self.console)
        self.troubleshooting_guide = TroubleshootingGuide(self.console)
        self.interactive_tutorial = InteractiveTutorial(self.console)
        self.example_generator = ExampleDataGenerator(self.console)
        self.comprehension_checker = ComprehensionChecker(self.console)

    def run(self) -> Optional[Dict[str, Any]]:
        """Run the interactive console UI."""
        if not RICH_AVAILABLE:
            return self._run_basic_ui()

        try:
            # Check if this is a first-time user and show adaptive welcome
            is_first_time = self.first_time_detector.is_first_time_user()
            user_level = self.first_time_detector.get_user_experience_level()
            
            # Check tutorial completion status
            tutorial_status = self.user_profiler.get_tutorial_completion_status()
            onboarding_completed = tutorial_status['onboarding_completed']
            
            if is_first_time or not onboarding_completed:
                # Show adaptive welcome for first-time or incomplete users
                welcome_result = self.adaptive_welcome.show_welcome(force_onboarding=True)
                
                # Offer tutorial for beginners or incomplete users
                if user_level == "beginner" or not onboarding_completed:
                    if self._offer_beginner_tutorial():
                        return None  # Tutorial completed, exit gracefully
                    else:
                        # If user skipped tutorial, still mark basic onboarding as complete
                        self._mark_basic_onboarding_complete()
            else:
                # Show standard welcome for returning users with completed onboarding
                self.ui_utils.show_welcome()
                
                # Subtle reminder about available help for returning users
                if RICH_AVAILABLE and self.console:
                    self.console.print("[dim]💡 Need help? Try option 4 (Tutorial) or 5 (Help) anytime![/dim]")
                    self.console.print()

            while True:
                choice = self._show_enhanced_main_menu(user_level)

                if choice == "1":
                    # Intelligent Packer (Smart Classification & Packaging)
                    try:
                        config = self.quick_start_wizard.run_wizard()
                        if config:
                            self._execute_quick_start_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Intelligent Packer wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
                elif choice == "2":
                    # Batch Mod Repacking
                    try:
                        config = self.batch_repack_wizard.run_wizard()
                        if config:
                            self._execute_batch_repack_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Batch repacking wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
                elif choice == "3":
                    # Advanced Classification (legacy - to be refactored)
                    try:
                        config = self._advanced_classification_wizard()
                        if config:
                            self._execute_quick_start_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Advanced classification wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
                elif choice == "4":
                    # Interactive Tutorial System
                    self._tutorial_menu()
                elif choice == "5":
                    # Help & Troubleshooting
                    self._enhanced_help_menu()
                elif choice == "6":
                    # Tools & Setup (legacy - to be refactored)
                    self._tools_menu()
                elif choice == "7" or choice.lower() == "q":
                    # Exit
                    self.console.print("[bold green]👋 Goodbye![/bold green]")
                    break
                else:
                    self.console.print("[red]❌ Invalid choice. Please try again.[/red]")
                    self.console.print()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
            return None
        except Exception as e:
            self.console.print(f"[red]❌ Unexpected error: {e}[/red]")
            return None

    def _run_basic_ui(self) -> Optional[Dict[str, Any]]:
        """Run basic UI when Rich is not available."""
        print("\n" + "=" * 60)
        print("🎮 Safe Resource Packer - The Complete Mod Packaging Solution")
        print("=" * 60)
        print("\n✨ Features:")
        print("• 🧠 Intelligent file classification")
        print("• 📦 Complete BSA/BA2 packaging")
        print("• 🚀 Batch processing capabilities")
        print("• 🎯 User-friendly interfaces")
        print("• ⚡ Performance optimized")
        print()

        while True:
            print("\n🎯 Main Menu")
            print("-" * 20)
            print("1. 🚀 Quick Start - File Packaging")
            print("2. 📦 Batch Repacking - Process Multiple Mods")
            print("3. 🔧 Advanced Classification")
            print("4. 🛠️ Tools & System")
            print("5. ❓ Help")
            print("6. 🚪 Exit")
            print()

            choice = input("Choose an option [1/2/3/4/5/6/q] (1): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', 'q', 'Q', '']:
                choice = choice if choice else '1'

                if choice == "1":
                    # Quick Start
                    config = self.quick_start_wizard.run_wizard() if self.quick_start_wizard else self._basic_quick_start()
                    if config:
                        self._execute_quick_start_processing_basic(config)
                elif choice == "2":
                    # Batch Repacking
                    config = self.batch_repack_wizard.run_wizard() if self.batch_repack_wizard else self._basic_batch_repacking()
                    if config:
                        self._execute_batch_repack_processing_basic(config)
                elif choice == "3":
                    # Advanced Classification
                    config = self._basic_classification()
                    if config:
                        self._execute_quick_start_processing_basic(config)
                elif choice == "4":
                    # Tools
                    self._tools_menu()
                elif choice == "5":
                    # Help
                    self._help_menu()
                elif choice == "6" or choice.lower() == "q":
                    print("\n👋 Goodbye!")
                    break
            else:
                print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, 6, or q")

    def _execute_quick_start_processing(self, config: Dict[str, Any]):
        """Execute Quick Start processing using QuickStartWizard service."""
        from .ui.quick_start_wizard import QuickStartWizard

        # Create wizard instance and execute processing
        wizard = QuickStartWizard(self.console)
        wizard.execute_processing(config)

    def _execute_quick_start_processing_basic(self, config: Dict[str, Any]):
        """Execute Quick Start processing using QuickStartWizard service (basic mode)."""
        from .ui.quick_start_wizard import QuickStartWizard

        # Create wizard instance and execute processing
        wizard = QuickStartWizard(self.console)
        wizard.execute_processing(config)

    def _execute_batch_repack_processing(self, config: Dict[str, Any]):
        """Execute batch repack processing using BatchRepackWizard service."""
        from .ui.batch_repack_wizard import BatchRepackWizard

        # Create wizard instance and execute processing
        wizard = BatchRepackWizard(self.console)
        wizard.execute_processing(config)

    def _execute_batch_repack_processing_basic(self, config: Dict[str, Any]):
        """Execute batch repack processing using BatchRepackWizard service (basic mode)."""
        from .ui.batch_repack_wizard import BatchRepackWizard

        # Create wizard instance and execute processing
        wizard = BatchRepackWizard(self.console)
        wizard.execute_processing(config)



    # Legacy methods - temporarily kept for functionality, to be refactored later
    def _advanced_classification_wizard(self) -> Optional[Dict[str, Any]]:
        """Advanced classification wizard (classification only)."""
        if not RICH_AVAILABLE:
            return self._basic_classification()

        # Beautiful header with examples
        header_panel = Panel.fit(
            "[bold bright_green]🔧 Advanced - File Classification Only[/bold bright_green]\n"
            "[dim]This will only classify files, not create packages[/dim]",
            border_style="bright_green",
            padding=(1, 2)
        )

        self.console.print(header_panel)
        self.console.print()

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

        # Show helpful explanation first
        self.console.print("[bold yellow]📋 What we need from you:[/bold yellow]")
        self.console.print("1. 📂 [bold]Source folder[/bold] - Your game's Data folder (contains vanilla game files)")
        self.console.print("2. 🔧 [bold]Generated folder[/bold] - Your mod files (BodySlide output, new mods, etc.)")
        self.console.print("3. 📁 [bold]Output folder[/bold] - Where we'll save the organized files")
        self.console.print()

        # Check for saved game paths first
        from .onboarding.user_profiler import UserProfiler
        saved_games = UserProfiler.get_available_game_paths()
        
        source = None
        if saved_games:
            self.console.print("[bold green]🎮 Found your games:[/bold green]")
            game_choices = {}
            for i, (game, path) in enumerate(saved_games.items(), 1):
                data_path = UserProfiler.get_game_data_path(game)
                if data_path:
                    self.console.print(f"  {i}. {game}: [cyan]{data_path}[/cyan]")
                    game_choices[str(i)] = data_path
            
            if game_choices:
                game_choices["custom"] = "Enter custom path"
                choice = Prompt.ask(
                    "\n[bold cyan]Select your game's Data folder[/bold cyan]",
                    choices=list(game_choices.keys()),
                    default="1" if "1" in game_choices else "custom"
                )
                
                if choice != "custom":
                    source = game_choices[choice]
                    self.console.print(f"[green]✅ Using: {source}[/green]")
        
        # If no saved games or user chose custom
        if not source:
            source = Prompt.ask(
                "[bold cyan]📂 Source files directory (Game Data folder)[/bold cyan]\n"
                "[dim]💡 This is your game's Data folder that contains vanilla game files.\n"
                "Examples:\n"
                "  • C:\\Steam\\steamapps\\common\\Skyrim Anniversary Edition\\Data\n"
                "  • C:\\Games\\Fallout 4\\Data\n"
                "  • D:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data\n"
                "💡 Tip: You can drag and drop the folder from Windows Explorer here[/dim]",
                default="",
                show_default=False
            )

        is_valid, result = self.ui_utils.validate_directory_path(source, "source directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        source = result

        # Get generated directory with better guidance
        generated = Prompt.ask(
            "[bold cyan]🔧 Generated files directory[/bold cyan]\n"
            "[dim]💡 This contains your mod files that you want to organize.\n"
            "Examples:\n"
            "  • C:\\Users\\YourName\\Documents\\My Games\\Skyrim Special Edition\\BodySlide\\Output\n"
            "  • C:\\Mods\\MyNewMod\n"
            "  • D:\\Downloads\\ModCollection\\WeaponPack\n"
            "💡 Tip: You can drag and drop the folder from Windows Explorer here[/dim]",
            default=""
        )

        is_valid, result = self.ui_utils.validate_directory_path(generated, "generated directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        generated = result

        # Single output directory - we'll create pack/loose subfolders automatically
        output_base = Prompt.ask(
            "[bold cyan]📁 Output directory (where organized files will be saved)[/bold cyan]\n"
            "[dim]💡 We'll automatically create 'pack' and 'loose' subfolders here.\n"
            "Examples:\n"
            "  • C:\\Users\\YourName\\Documents\\SafeResourcePacker\\Output\n"
            "  • D:\\Mods\\OrganizedMods\n"
            "  • .\\MyModPackage (current folder)\n"
            "💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./MyModPackage",
            show_default=True
        )

        # Automatically create pack and loose subfolders
        output_pack = os.path.join(output_base, "pack")
        output_loose = os.path.join(output_base, "loose")

        # Show what we'll create
        self.console.print(f"[green]✅ We'll create these folders automatically:[/green]")
        self.console.print(f"   📦 Pack files: {output_pack}")
        self.console.print(f"   📁 Loose files: {output_loose}")
        self.console.print()

        # Get optional settings
        threads = Prompt.ask("Number of threads", default="8")
        try:
            threads = int(threads)
        except ValueError:
            threads = 8

        debug = Confirm.ask("Enable debug mode? (recommended for troubleshooting)", default=True)

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

        config['source'] = input("Source files directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['source'] or not os.path.exists(config['source']):
            print("❌ Invalid source directory")
            return None

        config['generated'] = input("Generated files directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['generated'] or not os.path.exists(config['generated']):
            print("❌ Invalid generated directory")
            return None

        config['output_pack'] = input("Pack files output directory (💡 Tip: You can drag and drop a folder here): ").strip()
        if not config['output_pack']:
            print("❌ Pack output directory required")
            return None

        config['output_loose'] = input("Loose files output directory (💡 Tip: You can drag and drop a folder here): ").strip()
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
            print("3. Re-detect Game Installations")
            print("4. Back to Main Menu")
            choice = input("Choose an option (1-4): ").strip()

            if choice == "1":
                self._install_bsarch_basic()
            elif choice == "2":
                self._check_system_basic()
            elif choice == "3":
                self._redetect_games_basic()
            return

        while True:
            # Beautiful tools header
            tools_header = Panel.fit(
                "[bold bright_green]🛠️ Tools & Setup[/bold bright_green]\n"
                "[dim]System setup and tool installation[/dim]",
                border_style="bright_green",
                padding=(1, 2)
            )

            self.console.print(tools_header)
            self.console.print()

            # Enhanced tools menu with descriptions
            tools_text = """
[bold cyan]🔧 Available Tools[/bold cyan]

[bold green]1.[/bold green] [bold]Install BSArch[/bold]              [dim]→ Download and install BSArch for BSA/BA2 creation[/dim]
[bold green]2.[/bold green] [bold]Check System Setup[/bold]         [dim]→ Verify Python, Rich, and BSArch installation[/dim]
[bold green]3.[/bold green] [bold]Re-detect Game Installations[/bold] [dim]→ Scan system for game installations again[/dim]
[bold green]4.[/bold green] [bold]Back to Main Menu[/bold]          [dim]→ Return to the main menu[/dim]

[dim]💡 Tip: Re-run game detection if you installed games or moved them[/dim]
            """

            self.console.print(tools_text)
            self.console.print()
            choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"], default="1")

            if choice == "1":
                self._install_bsarch()
            elif choice == "2":
                self._check_system()
            elif choice == "3":
                self._redetect_games()
            elif choice == "4":
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
        print("Installing BSArch for optimal BSA/BA2 creation...\n")

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
        """Check system setup and dependencies."""
        if not RICH_AVAILABLE:
            return

        self.console.print("\n[bold blue]🔍 System Check[/bold blue]")
        self.console.print("[dim]Checking system setup and dependencies...[/dim]\n")

        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.console.print(f"[green]✅ Python {python_version}[/green]")

        # Check Rich
        try:
            import rich
            try:
                from rich import __version__ as rich_version
                self.console.print(f"[green]✅ Rich {rich_version}[/green]")
            except ImportError:
                # Fallback if __version__ not available
                self.console.print("[green]✅ Rich (version unknown)[/green]")
        except ImportError:
            self.console.print("[red]❌ Rich not available[/red]")

        # Check BSArch
        try:
            from .bsarch_detector import get_bsarch_detector
            detector = get_bsarch_detector()
            bsarch_path = detector.get_bsarch_path()
            if bsarch_path and os.path.exists(bsarch_path):
                self.console.print(f"[green]✅ BSArch found: {bsarch_path}[/green]")
            else:
                self.console.print("[yellow]⚠️ BSArch not found - install it for optimal archive creation[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error checking BSArch: {e}[/red]")

        self.console.print()

    def _check_system_basic(self):
        """Basic system check for when Rich is not available."""
        print("\n🔍 System Check")
        print("Checking system setup and dependencies...\n")

        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"✅ Python {python_version}")

        # Check Rich
        try:
            import rich
            try:
                from rich import __version__ as rich_version
                print(f"✅ Rich {rich_version}")
            except ImportError:
                # Fallback if __version__ not available
                print("✅ Rich (version unknown)")
        except ImportError:
            print("❌ Rich not available")

        # Check BSArch
        try:
            from .bsarch_detector import get_bsarch_detector
            detector = get_bsarch_detector()
            bsarch_path = detector.get_bsarch_path()
            if bsarch_path and os.path.exists(bsarch_path):
                print(f"✅ BSArch found: {bsarch_path}")
            else:
                print("⚠️ BSArch not found - install it for optimal archive creation")
        except Exception as e:
            print(f"❌ Error checking BSArch: {e}")

        print()

    def _redetect_games(self):
        """Re-run game detection to find newly installed or moved games."""
        if not RICH_AVAILABLE:
            return

        self.console.print("\n[bold blue]🔍 Game Detection[/bold blue]")
        self.console.print("[dim]Scanning system for game installations...[/dim]\n")
        self.console.print("[yellow]⚠️ This may take a few moments depending on your system.[/yellow]\n")

        try:
            # Force a fresh scan
            detected_games = self.user_profiler.detect_games(force_rescan=True)
            
            # Show results
            found_games = {name: path for name, path in detected_games.items() if path is not None}
            
            if found_games:
                self.console.print(f"[bold green]✅ Found {len(found_games)} game(s):[/bold green]\n")
                for game_name, game_path in found_games.items():
                    self.console.print(f"  [green]•[/green] {game_name}")
                    self.console.print(f"    [dim]{game_path}[/dim]")
                self.console.print()
                self.console.print("[green]💾 Game paths saved to your profile![/green]")
            else:
                self.console.print("[yellow]⚠️ No supported games found on this system.[/yellow]")
                self.console.print("[dim]Supported games: Skyrim SE/LE, Fallout 4, Fallout 76, Starfield[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Detection failed: {e}[/red]")
        
        self.console.print()
        input("Press Enter to continue...")

    def _redetect_games_basic(self):
        """Basic game re-detection for when Rich is not available."""
        print("\n🔍 Game Detection")
        print("Scanning system for game installations...")
        print("⚠️ This may take a few moments depending on your system.\n")

        try:
            # Force a fresh scan
            detected_games = self.user_profiler.detect_games(force_rescan=True)
            
            # Show results
            found_games = {name: path for name, path in detected_games.items() if path is not None}
            
            if found_games:
                print(f"✅ Found {len(found_games)} game(s):\n")
                for game_name, game_path in found_games.items():
                    print(f"  • {game_name}")
                    print(f"    {game_path}")
                print()
                print("💾 Game paths saved to your profile!")
            else:
                print("⚠️ No supported games found on this system.")
                print("Supported games: Skyrim SE/LE, Fallout 4, Fallout 76, Starfield")
            
        except Exception as e:
            print(f"❌ Detection failed: {e}")
        
        print()
        input("Press Enter to continue...")

    def _help_menu(self):
        """Help and information menu."""
        if not RICH_AVAILABLE:
            print("\n❓ Help & Information")
            print("=" * 25)
            print("Safe Resource Packer - The Complete Mod Packaging Solution")
            print("\nFeatures:")
            print("• 🧠 Intelligent file classification")
            print("• 📦 Complete BSA/BA2 packaging")
            print("• 🚀 Batch processing capabilities")
            print("• 🎯 User-friendly interfaces")
            print("• ⚡ Performance optimized")
            print("\nFor more information, visit: https://github.com/reidenxerx/safe-resource-packer")
            input("\nPress Enter to continue...")
            return

        # Beautiful help header
        help_header = Panel.fit(
            "[bold bright_blue]❓ Help & Information[/bold bright_blue]\n"
            "[dim]Learn more about Safe Resource Packer[/dim]",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(help_header)
        self.console.print()

        # Comprehensive help content
        help_content = """
[bold cyan]🎮 Safe Resource Packer - Complete Guide[/bold cyan]

[bold yellow]🎯 What This Tool Does:[/bold yellow]
• Takes your loose mod files (BodySlide output, new mods, etc.)
• Compares them against your game's vanilla files
• Creates optimized BSA/BA2 archives for better performance
• Keeps override files loose for proper modding
• Results in 60-70% faster loading times!

[bold cyan]📋 What You Need:[/bold cyan]
1. 📂 [bold]Source folder[/bold] - Your game's Data folder (contains vanilla files)
2. 🔧 [bold]Generated folder[/bold] - Your mod files (BodySlide output, new mods)
3. 📁 [bold]Output folder[/bold] - Where we'll save organized files

[bold magenta]🎮 Mod Manager Support:[/bold magenta]
[bold cyan]MO2 Users:[/bold cyan] Install directly in your main profile - it's safe!
[bold magenta]Vortex Users:[/bold magenta] Install through Vortex's mod installer
[bold green]Manual Users:[/bold green] Copy files directly to game Data folder

[bold green]💡 Tips:[/bold green]
• Start with option 1 (Intelligent Packer) for most users
• Use option 2 (Batch Repacking) for mod collections
• We create separate 'pack' and 'loose' folders automatically
• Enable debug mode for detailed logging
• Install BSArch for optimal archive creation

[bold red]🚨 Common Issues:[/bold red]
• "Python not found" → Install Python from python.org
• "Permission denied" → Run as administrator
• "Not enough space" → Free up disk space
• "BSArch not found" → Use Tools & System menu
        """

        help_panel = Panel(
            help_content,
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(help_panel)
        self.console.print()

        input("Press Enter to continue...")

    def _basic_quick_start(self) -> Optional[Dict[str, Any]]:
        """Basic Quick Start (legacy - to be refactored)."""
        # This will be moved to QuickStartWizard
        pass

    def _basic_batch_repacking(self) -> Optional[Dict[str, Any]]:
        """Basic Batch Repacking (legacy - to be refactored)."""
        # This will be moved to BatchRepackWizard
        pass

    # New noob-friendly methods
    def _offer_beginner_tutorial(self) -> bool:
        """Offer tutorial to beginner users."""
        try:
            if RICH_AVAILABLE and self.console:
                tutorial_panel = Panel(
                    "[bold bright_white]🎓 Welcome, New User![/bold bright_white]\n\n"
                    
                    "[bold yellow]🎯 Would you like a quick tutorial?[/bold yellow]\n"
                    "We can teach you everything you need to know in just 15 minutes!\n\n"
                    
                    "[bold green]📚 Tutorial Includes:[/bold green]\n"
                    "• Understanding what this tool does\n"
                    "• How to prepare your files\n"
                    "• What happens during processing\n"
                    "• How to install your results\n"
                    "• Practice with safe examples\n\n"
                    
                    "[bold cyan]💡 Benefits:[/bold cyan]\n"
                    "• Learn by doing with real examples\n"
                    "• Knowledge checks ensure understanding\n"
                    "• Build confidence before processing real mods\n"
                    "• Get tips from experienced modders\n\n"
                    
                    "[dim]You can always access the tutorial later from the main menu![/dim]",
                    border_style="bright_green",
                    padding=(1, 2),
                    title="🎓 Learning Opportunity"
                )
                self.console.print(tutorial_panel)
                
                if Confirm.ask("Start the interactive tutorial?", default=True):
                    self.interactive_tutorial.run_beginner_tutorial()
                    return True
            else:
                print("🎓 Welcome, New User!")
                print("Would you like a quick tutorial? (15 minutes)")
                print("We'll teach you everything you need to know!")
                print()
                
                response = input("Start tutorial? [Y/n]: ").strip().lower()
                if response == '' or response.startswith('y'):
                    self.interactive_tutorial.run_beginner_tutorial()
                    return True
            
            return False
            
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]❌ Tutorial error: {e}[/red]")
            else:
                print(f"❌ Tutorial error: {e}")
            return False
    
    def _mark_basic_onboarding_complete(self):
        """Mark basic onboarding as complete even if tutorial was skipped."""
        try:
            # Create a basic profile to indicate the user has been through onboarding
            self.first_time_detector.set_user_preferences(
                experience_level="intermediate",  # Assume intermediate if they skipped tutorial
                tutorial_completed=False  # They skipped it
            )
            
            # Also mark in user profiler that basic onboarding is done
            from datetime import datetime
            profile = self.user_profiler.load_user_profile()
            profile['onboarding_completed'] = True
            profile['onboarding_completion_date'] = datetime.now().isoformat()
            profile['tutorial_skipped'] = True
            self.user_profiler.save_user_preferences(profile)
            
        except Exception as e:
            # Don't fail if we can't save the profile
            pass
    
    def _show_enhanced_main_menu(self, user_level: str = "intermediate") -> str:
        """Show enhanced main menu with noob-friendly options."""
        if not RICH_AVAILABLE:
            return self._show_enhanced_main_menu_basic()
        
        # Customize menu based on user level
        tutorial_text = ""
        if user_level == "beginner":
            tutorial_text = " [dim](⭐ Recommended for beginners!)[/dim]"
        
        menu_panel = Panel(
            "[bold bright_white]🎯 Main Menu - Choose Your Task[/bold bright_white]\n\n"
            
            "[bold cyan]📋 MAIN FEATURES:[/bold cyan]\n"
            "[bold green]1.[/bold green] 🧠 [bold]Intelligent Packer[/bold] - [dim]Process YOUR files (BodySlide, custom content)[/dim]\n"
            "   [dim]→ Analyzes your generated files vs vanilla game files[/dim]\n"
            "   [dim]→ Creates optimized BSA/BA2 + loose file packages[/dim]\n"
            "   [dim]→ Perfect for BodySlide output, custom mods, texture packs[/dim]\n\n"
            
            "[bold green]2.[/bold green] 📦 [bold]Batch Repacker[/bold] - [dim]Repack EXISTING mods into archives[/dim]\n"
            "   [dim]→ Takes downloaded mods with loose files[/dim]\n"
            "   [dim]→ Converts them to BSA/BA2 format for performance[/dim]\n"
            "   [dim]→ Great for mod collections from Nexus[/dim]\n\n"
            
            "[bold green]3.[/bold green] 🔧 [bold]Advanced Options[/bold] - [dim]Fine-tune settings and rules[/dim]\n\n"
            
            "[bold cyan]📚 LEARNING & HELP:[/bold cyan]\n"
            f"[bold blue]4.[/bold blue] 🎓 [bold]Interactive Tutorial[/bold] - [dim]Learn everything step-by-step[/dim]{tutorial_text}\n"
            "[bold blue]5.[/bold blue] ❓ [bold]Help & Troubleshooting[/bold] - [dim]Get help with problems[/dim]\n\n"
            
            "[bold green]6.[/bold green] 🛠️ [bold]Tools & System[/bold] - [dim]Install BSArch, check requirements[/dim]\n"
            "[bold green]7.[/bold green] 🚪 [bold]Exit[/bold]\n\n"
            
            "[bold yellow]💡 Not sure which to choose?[/bold yellow]\n"
            "[dim]• Use [bold]Intelligent Packer[/bold] for YOUR created content (BodySlide, custom files)[/dim]\n"
            "[dim]• Use [bold]Batch Repacker[/bold] for downloaded mods you want to optimize[/dim]\n"
            f"[dim]• Try the [bold]Tutorial[/bold] first if you're new to this!{' (Recommended)' if user_level == 'beginner' else ''}[/dim]\n\n"
            
            "[bold red]⚠️ BODYSLIDE USERS - READ THIS:[/bold red]\n"
            "[dim]If your BodySlide outputs to your game Data folder mixed with other files,[/dim]\n"
            "[dim]our tool [bold]CANNOT[/bold] separate them! Use option 4 (Tutorial) to learn how to[/dim]\n"
            "[dim]set up clean BodySlide output for perfect results.[/dim]",
            border_style="bright_white",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        self.console.print()
        
        while True:
            choice = input("Choose an option [1/2/3/4/5/6/7/q] (1): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', 'q', 'Q', '']:
                return choice if choice else '1'
            print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, or q")
    
    def _show_enhanced_main_menu_basic(self) -> str:
        """Enhanced main menu for when Rich is not available."""
        print("\n🎯 Main Menu - Choose Your Task")
        print("=" * 35)
        print()
        print("📋 MAIN FEATURES:")
        print("1. 🧠 Intelligent Packer - Process YOUR files (BodySlide, custom content)")
        print("   → Analyzes your files vs vanilla game files")
        print("   → Perfect for BodySlide output, custom mods")
        print()
        print("2. 📦 Batch Repacker - Repack EXISTING mods into archives")
        print("   → Takes downloaded mods with loose files")
        print("   → Great for mod collections from Nexus")
        print()
        print("3. 🔧 Advanced Options - Fine-tune settings")
        print()
        print("📚 LEARNING & HELP:")
        print("4. 🎓 Interactive Tutorial - Learn everything step-by-step")
        print("5. ❓ Help & Troubleshooting - Get help with problems")
        print()
        print("6. 🛠️ Tools & System")
        print("7. 🚪 Exit")
        print()
        print("💡 Not sure which to choose?")
        print("• Use Intelligent Packer for YOUR created content")
        print("• Use Batch Repacker for downloaded mods you want to optimize")
        print("• Try the Tutorial first if you're new!")
        print()
        print("⚠️ BODYSLIDE USERS - READ THIS:")
        print("If your BodySlide outputs to your game Data folder mixed with other files,")
        print("our tool CANNOT separate them! Use option 4 (Tutorial) to learn how to")
        print("set up clean BodySlide output for perfect results.")
        print()
        
        while True:
            choice = input("Choose an option [1/2/3/4/5/6/7/q] (1): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', 'q', 'Q', '']:
                return choice if choice else '1'
            print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, or q")
    
    def _tutorial_menu(self):
        """Show tutorial and learning menu."""
        try:
            if RICH_AVAILABLE and self.console:
                tutorial_panel = Panel(
                    "[bold bright_white]🎓 Interactive Tutorial & Learning Center[/bold bright_white]\n\n"
                    
                    "[bold green]1.[/bold green] 📚 [bold]Complete Beginner Tutorial[/bold] - [dim]Full 15-minute guided experience[/dim]\n"
                    "[bold red]2.[/bold red] 🛠️ [bold]BodySlide Clean Output Setup[/bold] - [dim]Fix mixed files issue (IMPORTANT!)[/dim]\n"
                    "[bold cyan]3.[/bold cyan] 📦 [bold]Batch Repacker Guide[/bold] - [dim]Learn to repack downloaded mods[/dim]\n"
                    "[bold green]4.[/bold green] 🧠 [bold]Knowledge Checks[/bold] - [dim]Test your understanding on specific topics[/dim]\n"
                    "[bold green]5.[/bold green] 🎯 [bold]Practice Scenarios[/bold] - [dim]Safe examples to learn with[/dim]\n"
                    "[bold green]6.[/bold green] 📖 [bold]File Preparation Guide[/bold] - [dim]Learn to set up your folders correctly[/dim]\n"
                    "[bold green]7.[/bold green] 📋 [bold]Results Guide[/bold] - [dim]Understand and install your processed files[/dim]\n"
                    "[bold green]8.[/bold green] 🔙 [bold]Back to Main Menu[/bold]\n\n"
                    
                    "[bold yellow]💡 Recommendation:[/bold yellow] [dim]Start with option 1 for a complete learning experience![/dim]",
                    border_style="bright_blue",
                    padding=(1, 2),
                    title="🎓 Learning Center"
                )
                self.console.print(tutorial_panel)
                
                choice = input("Choose an option [1/2/3/4/5/6/7/8] (1): ").strip()
                if choice == '' or choice == '1':
                    self.interactive_tutorial.run_beginner_tutorial()
                elif choice == '2':
                    # Direct BodySlide setup guide
                    self.data_prep_guide._show_bodyslide_setup_guide()
                elif choice == '3':
                    # Batch Repacker onboarding guide
                    self._show_batch_repacker_guide()
                elif choice == '4':
                    self._knowledge_check_menu()
                elif choice == '5':
                    self._practice_scenarios_menu()
                elif choice == '6':
                    self.data_prep_guide.run_preparation_guide()
                elif choice == '7':
                    # Mock results for demo
                    mock_results = {
                        'pack_count': 1234,
                        'loose_count': 89,
                        'skip_count': 15,
                        'total_files': 1338
                    }
                    self.results_guide.show_results_explanation(mock_results, "C:\\ModPackages\\Example")
                elif choice == '8':
                    return
                else:
                    self.console.print("[red]❌ Invalid choice[/red]")
            else:
                print("🎓 Tutorial & Learning Menu")
                print("-" * 30)
                print("1. 📚 Complete Beginner Tutorial")
                print("2. 🛠️ BodySlide Clean Output Setup - Fix mixed files issue (IMPORTANT!)")
                print("3. 📦 Batch Repacker Guide - Learn to repack downloaded mods")
                print("4. 🧠 Knowledge Checks")
                print("5. 🎯 Practice Scenarios")
                print("6. 📖 File Preparation Guide")
                print("7. 📋 Results Guide")
                print("8. 🔙 Back to Main Menu")
                print()
                
                choice = input("Choose an option [1/2/3/4/5/6/7/8] (1): ").strip()
                if choice == '' or choice == '1':
                    self.interactive_tutorial.run_beginner_tutorial()
                elif choice == '2':
                    # Direct BodySlide setup guide
                    self.data_prep_guide._show_bodyslide_setup_guide()
                elif choice == '3':
                    # Batch Repacker onboarding guide
                    self._show_batch_repacker_guide()
                elif choice == '4':
                    self._knowledge_check_menu()
                elif choice == '5':
                    self._practice_scenarios_menu()
                elif choice == '6':
                    self.data_prep_guide.run_preparation_guide()
                elif choice == '7':
                    mock_results = {'pack_count': 1234, 'loose_count': 89, 'skip_count': 15, 'total_files': 1338}
                    self.results_guide.show_results_explanation(mock_results, "C:\\ModPackages\\Example")
                elif choice == '8':
                    return
                else:
                    print("❌ Invalid choice")
                    
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]❌ Tutorial menu error: {e}[/red]")
            else:
                print(f"❌ Tutorial menu error: {e}")
    
    def _knowledge_check_menu(self):
        """Show knowledge check options."""
        try:
            topics = self.comprehension_checker.show_available_topics()
            
            if RICH_AVAILABLE and self.console:
                self.console.print("\n[bold cyan]Select a topic to test your knowledge:[/bold cyan]")
                for i, topic in enumerate(topics, 1):
                    self.console.print(f"{i}. {topic.title()}")
                self.console.print(f"{len(topics) + 1}. Back")
                
                choice = input(f"Choose [1-{len(topics) + 1}]: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(topics):
                        topic = topics[choice_num - 1]
                        score, total, passed = self.comprehension_checker.run_knowledge_check(topic)
                        if passed:
                            self.console.print(f"[bold green]🎉 Congratulations! You passed the {topic} knowledge check![/bold green]")
                        else:
                            self.console.print(f"[bold yellow]📚 Consider reviewing {topic} concepts and trying again.[/bold yellow]")
                except ValueError:
                    self.console.print("[red]❌ Invalid choice[/red]")
            else:
                print("\nSelect a topic to test your knowledge:")
                for i, topic in enumerate(topics, 1):
                    print(f"{i}. {topic.title()}")
                print(f"{len(topics) + 1}. Back")
                
                choice = input(f"Choose [1-{len(topics) + 1}]: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(topics):
                        topic = topics[choice_num - 1]
                        score, total, passed = self.comprehension_checker.run_knowledge_check(topic)
                        if passed:
                            print(f"🎉 Congratulations! You passed the {topic} knowledge check!")
                        else:
                            print(f"📚 Consider reviewing {topic} concepts and trying again.")
                except ValueError:
                    print("❌ Invalid choice")
                    
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]❌ Knowledge check error: {e}[/red]")
            else:
                print(f"❌ Knowledge check error: {e}")
    
    def _practice_scenarios_menu(self):
        """Show practice scenarios menu."""
        try:
            scenarios = self.example_generator.show_available_scenarios()
            
            if RICH_AVAILABLE and self.console:
                self.console.print("\n[bold cyan]Choose a practice scenario:[/bold cyan]")
                for i, scenario in enumerate(scenarios, 1):
                    scenario_info = self.example_generator.scenarios[scenario]
                    self.console.print(f"{i}. [bold]{scenario_info['name']}[/bold] - {scenario_info.get('description', 'No description')}")
                self.console.print(f"{len(scenarios) + 1}. Back")
                
                choice = input(f"Choose [1-{len(scenarios) + 1}]: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(scenarios):
                        scenario_name = scenarios[choice_num - 1]
                        paths = self.example_generator.create_practice_scenario(scenario_name)
                        if paths:
                            self.console.print(f"[bold green]✅ Practice scenario created![/bold green]")
                            self.console.print(f"[bold cyan]📁 Practice folder:[/bold cyan] {paths['base']}")
                            self.console.print("[bold yellow]💡 You can now use the main tool with these safe practice files![/bold yellow]")
                            
                            if Confirm.ask("Clean up practice files now?", default=False):
                                self.example_generator.cleanup_scenario(paths)
                except ValueError:
                    self.console.print("[red]❌ Invalid choice[/red]")
            else:
                print("\nChoose a practice scenario:")
                for i, scenario in enumerate(scenarios, 1):
                    scenario_info = self.example_generator.scenarios[scenario]
                    print(f"{i}. {scenario_info['name']} - {scenario_info.get('description', 'No description')}")
                print(f"{len(scenarios) + 1}. Back")
                
                choice = input(f"Choose [1-{len(scenarios) + 1}]: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(scenarios):
                        scenario_name = scenarios[choice_num - 1]
                        paths = self.example_generator.create_practice_scenario(scenario_name)
                        if paths:
                            print("✅ Practice scenario created!")
                            print(f"📁 Practice folder: {paths['base']}")
                            print("💡 You can now use the main tool with these safe practice files!")
                            
                            cleanup = input("Clean up practice files now? [y/N]: ").strip().lower()
                            if cleanup.startswith('y'):
                                self.example_generator.cleanup_scenario(paths)
                except ValueError:
                    print("❌ Invalid choice")
                    
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]❌ Practice scenarios error: {e}[/red]")
            else:
                print(f"❌ Practice scenarios error: {e}")
    
    def _show_batch_repacker_guide(self):
        """Show comprehensive Batch Repacker onboarding guide."""
        try:
            if RICH_AVAILABLE and self.console:
                guide_panel = Panel(
                    "[bold bright_white]📦 Batch Repacker - Complete Guide[/bold bright_white]\n\n"
                    
                    "[bold yellow]🎯 What is Batch Repacker?[/bold yellow]\n"
                    "• Converts downloaded mods with loose files into BSA/BA2 archives\n"
                    "• [bold red]REQUIRES:[/bold red] Mods must already have ESP/ESL/ESM plugins\n"
                    "• Processes multiple mod folders automatically\n"
                    "• Improves game performance by reducing file system overhead\n"
                    "• Perfect for mod collections from Nexus Mods\n\n"
                    
                    "[bold green]📋 Perfect Use Cases:[/bold green]\n"
                    "• Any downloaded mod with ESP/ESL/ESM + loose files\n"
                    "• Texture overhauls, armor packs, weapon collections\n"
                    "• Quest mods, gameplay overhauls, animation packs\n"
                    "• Environmental mods, sound packs, script-heavy mods\n"
                    "• Basically: [bold]Any mod with plugin + loose assets[/bold]\n\n"
                    
                    "[bold red]❌ NOT for:[/bold red]\n"
                    "• YOUR created content (use Intelligent Packer instead)\n"
                    "• BodySlide output (use Intelligent Packer)\n"
                    "• Mods that already have BSA/BA2 files\n"
                    "• [bold]Mods without ESP/ESL/ESM plugins[/bold] (no way to load archives)\n"
                    "• Pure texture/mesh packs without plugins\n\n"
                    
                    "[bold blue]🔧 How It Works:[/bold blue]\n"
                    "1. Point to folder containing multiple mod folders\n"
                    "2. Tool scans for mods that have ESP/ESL/ESM plugins\n"
                    "3. Creates BSA/BA2 archives from their loose files\n"
                    "4. Updates existing plugins to reference the new archives\n"
                    "5. Organizes everything in clean output structure\n\n"
                    
                    "[bold cyan]📁 Expected Folder Structure:[/bold cyan]\n"
                    "ModsFolder/\n"
                    "├── ArmorMod1/\n"
                    "│   ├── ArmorMod1.esp ← [bold]Required![/bold]\n"
                    "│   ├── textures/\n"
                    "│   └── meshes/\n"
                    "├── QuestMod2/\n"
                    "│   ├── QuestMod2.esm ← [bold]Required![/bold]\n"
                    "│   ├── scripts/\n"
                    "│   └── sounds/\n"
                    "└── WeaponPack3/\n"
                    "    ├── WeaponPack3.esp ← [bold]Required![/bold]\n"
                    "    ├── textures/\n"
                    "    └── meshes/\n\n"
                    
                    "[bold magenta]🎮 After Processing:[/bold magenta]\n"
                    "• Each mod gets its own BSA/BA2 file\n"
                    "• Existing ESP/ESL/ESM files updated to reference archives\n"
                    "• Ready to install in mod manager\n"
                    "• Massive performance improvement\n\n"
                    
                    "[bold yellow]💡 Pro Tips:[/bold yellow]\n"
                    "• Process similar mod types together (all textures, all meshes)\n"
                    "• Use descriptive output folder names\n"
                    "• Check results before installing in game\n"
                    "• Keep original mods as backup",
                    border_style="bright_cyan",
                    padding=(1, 2),
                    title="📦 Batch Repacker Guide"
                )
                self.console.print(guide_panel)
                
                if Confirm.ask("\n[bold green]Ready to try Batch Repacker now?[/bold green]", default=False):
                    return self._run_batch_repacking()
                    
            else:
                print("📦 Batch Repacker - Complete Guide")
                print("=" * 40)
                print()
                print("🎯 What is Batch Repacker?")
                print("• Converts downloaded mods with loose files into BSA/BA2 archives")
                print("• REQUIRES: Mods must already have ESP/ESL/ESM plugins")
                print("• Processes multiple mod folders automatically")
                print("• Improves game performance by reducing file system overhead")
                print("• Perfect for mod collections from Nexus Mods")
                print()
                print("📋 Perfect Use Cases:")
                print("• Any downloaded mod with ESP/ESL/ESM + loose files")
                print("• Texture overhauls, armor packs, weapon collections")
                print("• Quest mods, gameplay overhauls, animation packs")
                print("• Environmental mods, sound packs, script-heavy mods")
                print("• Basically: Any mod with plugin + loose assets")
                print()
                print("❌ NOT for:")
                print("• YOUR created content (use Intelligent Packer instead)")
                print("• BodySlide output (use Intelligent Packer)")
                print("• Mods that already have BSA/BA2 files")
                print("• Mods without ESP/ESL/ESM plugins (no way to load archives)")
                print("• Pure texture/mesh packs without plugins")
                print()
                print("🔧 How It Works:")
                print("1. Point to folder containing multiple mod folders")
                print("2. Tool scans for mods that have ESP/ESL/ESM plugins")
                print("3. Creates BSA/BA2 archives from their loose files")
                print("4. Updates existing plugins to reference the new archives")
                print("5. Organizes everything in clean output structure")
                print()
                print("💡 Pro Tips:")
                print("• Process similar mod types together")
                print("• Use descriptive output folder names")
                print("• Check results before installing in game")
                print("• Keep original mods as backup")
                print()
                
                choice = input("Ready to try Batch Repacker now? [y/N]: ").strip().lower()
                if choice in ['y', 'yes']:
                    return self._run_batch_repacking()
                    
        except Exception as e:
            print(f"Error showing Batch Repacker guide: {e}")
    
    def _enhanced_help_menu(self):
        """Show enhanced help menu with troubleshooting."""
        try:
            action = self.troubleshooting_guide.show_help_menu()
            
            if action == "back_to_main":
                return
            elif action in ["cancelled", "error"]:
                if RICH_AVAILABLE and self.console:
                    self.console.print("[yellow]Returning to main menu...[/yellow]")
                else:
                    print("Returning to main menu...")
                    
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]❌ Help menu error: {e}[/red]")
            else:
                print(f"❌ Help menu error: {e}")


def run_console_ui() -> Optional[Dict[str, Any]]:
    """Run the console UI."""
    ui = ConsoleUI()
    return ui.run()


if __name__ == "__main__":
    run_console_ui()
