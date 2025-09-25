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
            
            if is_first_time:
                # Show adaptive welcome for first-time users
                self.adaptive_welcome.show_welcome(user_level)
                
                # Offer tutorial for beginners
                if user_level == "beginner":
                    if self._offer_beginner_tutorial():
                        return None  # Tutorial completed, exit gracefully
            else:
                # Show standard welcome for returning users
                self.ui_utils.show_welcome()

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

        # Get source directory with better guidance
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
            print("3. Back to Main Menu")
            choice = input("Choose an option (1-3): ").strip()

            if choice == "1":
                self._install_bsarch_basic()
            elif choice == "2":
                self._check_system_basic()
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
[bold green]3.[/bold green] [bold]Back to Main Menu[/bold]          [dim]→ Return to the main menu[/dim]

[dim]💡 Tip: Install BSArch first for optimal archive creation[/dim]
            """

            self.console.print(tools_text)
            self.console.print()
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
            self.console.print(f"[green]✅ Rich {rich.__version__}[/green]")
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
            print(f"✅ Rich {rich.__version__}")
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
    
    def _show_enhanced_main_menu(self, user_level: str = "intermediate") -> str:
        """Show enhanced main menu with noob-friendly options."""
        if not RICH_AVAILABLE:
            return self._show_enhanced_main_menu_basic()
        
        # Customize menu based on user level
        tutorial_text = ""
        if user_level == "beginner":
            tutorial_text = " [dim](⭐ Recommended for beginners!)[/dim]"
        
        menu_panel = Panel(
            "[bold bright_white]🎯 Main Menu[/bold bright_white]\n\n"
            "[bold green]1.[/bold green] 🧠 [bold]Intelligent Packer[/bold] - [dim]Smart file classification & complete packaging (recommended)[/dim]\n"
            "[bold green]2.[/bold green] 📦 [bold]Batch Repacking[/bold] - [dim]Process multiple mods at once (collections)[/dim]\n"
            "[bold green]3.[/bold green] 🔧 [bold]Advanced Classification[/bold] - [dim]Fine-tune settings and rules[/dim]\n"
            f"[bold blue]4.[/bold blue] 🎓 [bold]Interactive Tutorial[/bold] - [dim]Learn step-by-step with examples[/dim]{tutorial_text}\n"
            "[bold blue]5.[/bold blue] ❓ [bold]Help & Troubleshooting[/bold] - [dim]Get help with problems and questions[/dim]\n"
            "[bold green]6.[/bold green] 🛠️ [bold]Tools & System[/bold] - [dim]Install BSArch, check requirements[/dim]\n"
            "[bold green]7.[/bold green] 🚪 [bold]Exit[/bold] - [dim]Close the application[/dim]\n\n"
            "[bold yellow]💡 Tip:[/bold yellow] [dim]New users should try the tutorial first, then use option 1 for most tasks[/dim]",
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
        print("\n🎯 Main Menu")
        print("-" * 20)
        print("1. 🧠 Intelligent Packer - Smart File Classification & Packaging")
        print("2. 📦 Batch Repacking - Process Multiple Mods")
        print("3. 🔧 Advanced Classification")
        print("4. 🎓 Interactive Tutorial - Learn Step-by-Step")
        print("5. ❓ Help & Troubleshooting")
        print("6. 🛠️ Tools & System")
        print("7. 🚪 Exit")
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
                    "[bold green]2.[/bold green] 🧠 [bold]Knowledge Checks[/bold] - [dim]Test your understanding on specific topics[/dim]\n"
                    "[bold green]3.[/bold green] 🎯 [bold]Practice Scenarios[/bold] - [dim]Safe examples to learn with[/dim]\n"
                    "[bold green]4.[/bold green] 📖 [bold]File Preparation Guide[/bold] - [dim]Learn to set up your folders correctly[/dim]\n"
                    "[bold green]5.[/bold green] 📋 [bold]Results Guide[/bold] - [dim]Understand and install your processed files[/dim]\n"
                    "[bold green]6.[/bold green] 🔙 [bold]Back to Main Menu[/bold]\n\n"
                    
                    "[bold yellow]💡 Recommendation:[/bold yellow] [dim]Start with option 1 for a complete learning experience![/dim]",
                    border_style="bright_blue",
                    padding=(1, 2),
                    title="🎓 Learning Center"
                )
                self.console.print(tutorial_panel)
                
                choice = input("Choose an option [1/2/3/4/5/6] (1): ").strip()
                if choice == '' or choice == '1':
                    self.interactive_tutorial.run_beginner_tutorial()
                elif choice == '2':
                    self._knowledge_check_menu()
                elif choice == '3':
                    self._practice_scenarios_menu()
                elif choice == '4':
                    self.data_prep_guide.run_preparation_guide()
                elif choice == '5':
                    # Mock results for demo
                    mock_results = {
                        'pack_count': 1234,
                        'loose_count': 89,
                        'skip_count': 15,
                        'total_files': 1338
                    }
                    self.results_guide.show_results_explanation(mock_results, "C:\\ModPackages\\Example")
                elif choice == '6':
                    return
                else:
                    self.console.print("[red]❌ Invalid choice[/red]")
            else:
                print("🎓 Tutorial & Learning Menu")
                print("-" * 30)
                print("1. 📚 Complete Beginner Tutorial")
                print("2. 🧠 Knowledge Checks")
                print("3. 🎯 Practice Scenarios")
                print("4. 📖 File Preparation Guide")
                print("5. 📋 Results Guide")
                print("6. 🔙 Back to Main Menu")
                print()
                
                choice = input("Choose an option [1/2/3/4/5/6] (1): ").strip()
                if choice == '' or choice == '1':
                    self.interactive_tutorial.run_beginner_tutorial()
                elif choice == '2':
                    self._knowledge_check_menu()
                elif choice == '3':
                    self._practice_scenarios_menu()
                elif choice == '4':
                    self.data_prep_guide.run_preparation_guide()
                elif choice == '5':
                    mock_results = {'pack_count': 1234, 'loose_count': 89, 'skip_count': 15, 'total_files': 1338}
                    self.results_guide.show_results_explanation(mock_results, "C:\\ModPackages\\Example")
                elif choice == '6':
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
