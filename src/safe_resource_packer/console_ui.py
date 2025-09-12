"""
Simplified Console UI - Clean, minimal interactive interface

Provides a simple, user-friendly interface that runs on top of the CLI system.
Users can select options through menus instead of remembering command-line flags.

Naming Conventions:
- Functions with 'quick_start_' prefix: Used for Quick Start mode (single mod processing)
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


class ConsoleUI:
    """Simplified Console UI using modular components."""
    
    def __init__(self):
        """Initialize Console UI."""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Initialize UI components
        self.ui_utils = UIUtilities(self.console) if RICH_AVAILABLE else None
        self.quick_start_wizard = QuickStartWizard(self.console) if RICH_AVAILABLE else None
        self.batch_repack_wizard = BatchRepackWizard(self.console) if RICH_AVAILABLE else None

    def run(self) -> Optional[Dict[str, Any]]:
        """Run the interactive console UI."""
        if not RICH_AVAILABLE:
            return self._run_basic_ui()

        try:
            self.ui_utils.show_welcome()

            while True:
                choice = self.ui_utils.show_main_menu()

                if choice == "1":
                    # Quick Start (Packaging)
                    try:
                        config = self.quick_start_wizard.run_wizard()
                        if config:
                            self._execute_quick_start_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Quick start wizard failed: {e}[/red]")
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
                    # Tools & Setup (legacy - to be refactored)
                    self._tools_menu()
                elif choice == "5":
                    # Help & Info (legacy - to be refactored)
                    self._help_menu()
                elif choice == "6" or choice.lower() == "q":
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
        """Execute Quick Start processing with Rich UI."""
        from .core import SafeResourcePacker
        from .packaging.package_builder import PackageBuilder
        from .config_cache import get_config_cache
        
        # Show processing header
        self.ui_utils.show_processing_header(config)
        
        # Save configuration
        config_cache = get_config_cache()
        config_cache.save_config(config)
        
        # Initialize packer
        packer = SafeResourcePacker(
            threads=config.get('threads', 8),
            debug=config.get('debug', False),
            game_type=config.get('game_type', 'skyrim')
        )
        
        # Process resources
        pack_count, loose_count, blacklisted_count, skip_count = packer.process_single_mod_resources(
            source_path=config['source'],
            generated_path=config['generated'],
            output_pack=config['output_pack'],
            output_loose=config['output_loose'],
            output_blacklisted=config['output_blacklisted']
        )
        
        # Show results
        self.console.print(f"\n[bold green]✅ Classification Complete![/bold green]")
        self.console.print(f"📦 Files to pack: {pack_count}")
        self.console.print(f"📁 Files to keep loose: {loose_count}")
        self.console.print(f"🚫 Blacklisted files: {blacklisted_count}")
        self.console.print(f"⏭️ Files skipped (identical): {skip_count}")
        
        if pack_count > 0 or loose_count > 0 or blacklisted_count > 0:
            if Confirm.ask("\nProceed with packaging?", default=True):
                self._handle_packaging(config, pack_count, loose_count, blacklisted_count, skip_count)
        else:
            self.console.print("\n[yellow]⚠️ No files to process![/yellow]")
        
        input("\nPress Enter to continue...")

    def _execute_quick_start_processing_basic(self, config: Dict[str, Any]):
        """Execute Quick Start processing with basic UI."""
        from .core import SafeResourcePacker
        from .packaging.package_builder import PackageBuilder
        from .config_cache import get_config_cache
        
        print("\n🚀 Starting Processing")
        print("-" * 30)
        print(f"📁 Source: {config.get('source', 'N/A')}")
        print(f"🔧 Generated: {config.get('generated', 'N/A')}")
        print(f"📦 Pack Output: {config.get('output_pack', 'N/A')}")
        print(f"📁 Loose Output: {config.get('output_loose', 'N/A')}")
        print(f"⚡ Threads: {config.get('threads', 8)}")
        print(f"🐛 Debug: {'Yes' if config.get('debug', False) else 'No'}")
        print()
        
        # Save configuration
        config_cache = get_config_cache()
        config_cache.save_config(config)
        
        # Initialize packer
        packer = SafeResourcePacker(
            threads=config.get('threads', 8),
            debug=config.get('debug', False),
            game_type=config.get('game_type', 'skyrim')
        )
        
        # Process resources
        pack_count, loose_count, blacklisted_count, skip_count = packer.process_single_mod_resources(
            source_path=config['source'],
            generated_path=config['generated'],
            output_pack=config['output_pack'],
            output_loose=config['output_loose'],
            output_blacklisted=config['output_blacklisted']
        )
        
        # Show results
        print(f"\n✅ Classification Complete!")
        print(f"📦 Files to pack: {pack_count}")
        print(f"📁 Files to keep loose: {loose_count}")
        print(f"🚫 Blacklisted files: {blacklisted_count}")
        print(f"⏭️ Files skipped (identical): {skip_count}")
        
        if pack_count > 0 or loose_count > 0 or blacklisted_count > 0:
            if input("\nProceed with packaging? [Y/n]: ").strip().lower() not in ['n', 'no']:
                self._handle_packaging_basic(config, pack_count, loose_count, blacklisted_count, skip_count)
        else:
            print("\n⚠️ No files to process!")
        
        input("\nPress Enter to continue...")

    def _execute_batch_repack_processing(self, config: Dict[str, Any]):
        """Execute Batch Repack processing with Rich UI."""
        from .batch_repacker import BatchModRepacker
        
        self.console.print(f"\n[bold green]🚀 Starting Batch Repacking[/bold green]")
        self.console.print(f"📁 Collection: {config['collection']}")
        self.console.print(f"🎮 Game: {config['game_type']}")
        self.console.print(f"⚡ Threads: {config['threads']}")
        self.console.print()
        
        # Initialize batch repacker
        repacker = BatchModRepacker(
            game_type=config['game_type'],
            threads=config['threads']
        )
        
        # Process mods
        results = repacker.process_mods(
            collection_path=config['collection'],
            output_path=os.path.join(config['collection'], "repacked")
        )
        
        # Show results
        self.console.print(f"\n[bold green]✅ Batch Repacking Complete![/bold green]")
        self.console.print(f"✅ Successful: {results.get('successful', 0)}")
        self.console.print(f"❌ Failed: {results.get('failed', 0)}")
        self.console.print(f"⏭️ Skipped: {results.get('skipped', 0)}")
        
        input("\nPress Enter to continue...")

    def _execute_batch_repack_processing_basic(self, config: Dict[str, Any]):
        """Execute Batch Repack processing with basic UI."""
        from .batch_repacker import BatchModRepacker
        
        print(f"\n🚀 Starting Batch Repacking")
        print(f"📁 Collection: {config['collection']}")
        print(f"🎮 Game: {config['game_type']}")
        print(f"⚡ Threads: {config['threads']}")
        print()
        
        # Initialize batch repacker
        repacker = BatchModRepacker(
            game_type=config['game_type'],
            threads=config['threads']
        )
        
        # Process mods
        results = repacker.process_mods(
            collection_path=config['collection'],
            output_path=os.path.join(config['collection'], "repacked")
        )
        
        # Show results
        print(f"\n✅ Batch Repacking Complete!")
        print(f"✅ Successful: {results.get('successful', 0)}")
        print(f"❌ Failed: {results.get('failed', 0)}")
        print(f"⏭️ Skipped: {results.get('skipped', 0)}")
        
        input("\nPress Enter to continue...")

    def _handle_packaging(self, config: Dict[str, Any], pack_count: int, loose_count: int, blacklisted_count: int, skip_count: int, pack_files: List[str] = None, loose_files: List[str] = None, blacklisted_files: List[str] = None):
        """Handle packaging with Rich UI."""
        from .packaging.package_builder import PackageBuilder
        
        self.console.print(f"\n[bold cyan]📦 Starting Packaging Process[/bold cyan]")
        
        # Initialize package builder
        package_builder = PackageBuilder(
            game_type=config.get('game_type', 'skyrim'),
            compression_level=config.get('compression', 5)
        )
        
        # Build package
        success, package_info = package_builder.build_complete_package(
            mod_name=os.path.basename(config['generated']),
            source_path=config['source'],
            generated_path=config['generated'],
            output_path=os.path.dirname(config['output_pack']),
            options={
                'output_pack': config['output_pack'],
                'output_loose': config['output_loose'],
                'output_blacklisted': config['output_blacklisted'],
                'threads': config.get('threads', 8),
                'debug': config.get('debug', False)
            }
        )
        
        if success:
            self.console.print(f"\n[bold green]✅ Packaging Complete![/bold green]")
            if package_info.get("components", {}).get("pack"):
                self.console.print(f"📦 Packed archive: {os.path.basename(package_info['components']['pack']['path'])}")
            if package_info.get("components", {}).get("loose"):
                self.console.print(f"📁 Loose archive: {os.path.basename(package_info['components']['loose']['path'])}")
        else:
            self.console.print(f"\n[bold red]❌ Packaging Failed![/bold red]")
            self.console.print(f"Error: {package_info}")

    def _handle_packaging_basic(self, config: Dict[str, Any], pack_count: int, loose_count: int, blacklisted_count: int, skip_count: int, pack_files: List[str] = None, loose_files: List[str] = None, blacklisted_files: List[str] = None):
        """Handle packaging with basic UI."""
        from .packaging.package_builder import PackageBuilder
        
        print(f"\n📦 Starting Packaging Process")
        
        # Initialize package builder
        package_builder = PackageBuilder(
            game_type=config.get('game_type', 'skyrim'),
            compression_level=config.get('compression', 5)
        )
        
        # Build package
        success, package_info = package_builder.build_complete_package(
            mod_name=os.path.basename(config['generated']),
            source_path=config['source'],
            generated_path=config['generated'],
            output_path=os.path.dirname(config['output_pack']),
            options={
                'output_pack': config['output_pack'],
                'output_loose': config['output_loose'],
                'output_blacklisted': config['output_blacklisted'],
                'threads': config.get('threads', 8),
                'debug': config.get('debug', False)
            }
        )
        
        if success:
            print(f"\n✅ Packaging Complete!")
            if package_info.get("components", {}).get("pack"):
                print(f"📦 Packed archive: {os.path.basename(package_info['components']['pack']['path'])}")
            if package_info.get("components", {}).get("loose"):
                print(f"📁 Loose archive: {os.path.basename(package_info['components']['loose']['path'])}")
        else:
            print(f"\n❌ Packaging Failed!")
            print(f"Error: {package_info}")

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

        # Get source directory
        source = Prompt.ask(
            "[bold cyan]📂 Source files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default=""
        )
        
        is_valid, result = self.ui_utils.validate_directory_path(source, "source directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        source = result

        # Get generated directory
        generated = Prompt.ask(
            "[bold cyan]📂 Generated files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default=""
        )
        
        is_valid, result = self.ui_utils.validate_directory_path(generated, "generated directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        generated = result

        # Get output directories
        output_pack = Prompt.ask(
            "[bold cyan]📦 Pack files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./pack"
        )
        output_loose = Prompt.ask(
            "[bold cyan]📁 Loose files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default="./loose"
        )

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
        
        # Help content
        help_content = """
[bold cyan]🎮 Safe Resource Packer[/bold cyan]

[bold green]✨ Features:[/bold green]
• 🧠 Intelligent file classification
• 📦 Complete BSA/BA2 packaging  
• 🚀 Batch processing capabilities
• 🎯 User-friendly interfaces
• ⚡ Performance optimized

[bold green]📚 Documentation:[/bold green]
• GitHub: https://github.com/reidenxerx/safe-resource-packer
• Docs: https://reidenxerx.github.io/safe-resource-packer/

[bold green]🆘 Support:[/bold green]
• Issues: https://github.com/reidenxerx/safe-resource-packer/issues
• Discussions: https://github.com/reidenxerx/safe-resource-packer/discussions

[bold green]💡 Tips:[/bold green]
• Use Quick Start for single mod processing
• Use Batch Repacking for multiple mods
• Install BSArch for optimal archive creation
• Enable debug mode for detailed logging
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


def run_console_ui() -> Optional[Dict[str, Any]]:
    """Run the console UI."""
    ui = ConsoleUI()
    return ui.run()


if __name__ == "__main__":
    run_console_ui()
