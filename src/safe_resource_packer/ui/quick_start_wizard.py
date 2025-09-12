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

from ..config_service import ConfigService


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
        # Use centralized configuration service
        config_service = ConfigService(self.console)
        return config_service.collect_quick_start_config(use_cached=True)

    def _basic_quick_start(self) -> Optional[Dict[str, Any]]:
        """Basic Quick Start for when Rich is not available."""
        # Use centralized configuration service
        config_service = ConfigService(None)  # No console for basic mode
        return config_service.collect_quick_start_config(use_cached=True)

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
    
    def execute_processing(self, config: Dict[str, Any]) -> None:
        """Execute Quick Start processing with Rich UI."""
        if not RICH_AVAILABLE:
            self._execute_quick_start_processing_basic(config)
            return
            
        from ..core import SafeResourcePacker
        from ..packaging.package_builder import PackageBuilder
        from ..config_cache import get_config_cache
        from ..dynamic_progress import enable_dynamic_progress, create_clean_progress_callback
        from ..dynamic_progress import enhance_classifier_output
        from rich.panel import Panel
        from rich.prompt import Confirm
        import os
        
        # Enable dynamic progress
        enable_dynamic_progress(True)
        
        # Show processing header
        self._show_processing_header(config)
        
        # Save configuration
        config_cache = get_config_cache()
        config_cache.save_config(config)
        
        # Initialize packer
        packer = SafeResourcePacker(
            threads=config.get('threads', 8),
            debug=config.get('debug', False),
            game_type=config.get('game_type', 'skyrim')
        )
        
        # Enhance classifier for beautiful output
        enhance_classifier_output(packer.classifier, quiet=False)
        
        # Create progress callback
        progress_callback = create_clean_progress_callback(self.console, quiet=False)
        
        # Process resources with beautiful progress
        pack_count, loose_count, blacklisted_count, skip_count = packer.process_single_mod_resources(
            source_path=config['source'],
            generated_path=config['generated'],
            output_pack=config['output_pack'],
            output_loose=config['output_loose'],
            output_blacklisted=config['output_blacklisted'],
            progress_callback=progress_callback
        )
        
        # Show classification results
        results_panel = Panel.fit(
            f"🎉 [bold bright_green]Classification Complete![/bold bright_green]\n\n"
            f"📦 [bold blue]Files to Pack:[/bold blue] {pack_count:,}\n"
            f"📁 [bold magenta]Files to Keep Loose:[/bold magenta] {loose_count:,}\n"
            f"🚫 [bold red]Blacklisted Files:[/bold red] {blacklisted_count:,}\n"
            f"⏭️ [bold yellow]Files Skipped:[/bold yellow] {skip_count:,}",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(results_panel)
        self.console.print()
        
        if pack_count > 0 or loose_count > 0 or blacklisted_count > 0:
            if Confirm.ask("Create complete mod package?", default=True):
                # Collect file lists from output directories
                current_pack_files = []
                current_loose_files = []
                current_blacklisted_files = []
                
                if pack_count > 0 and os.path.exists(config['output_pack']):
                    for root, dirs, files in os.walk(config['output_pack']):
                        for file in files:
                            current_pack_files.append(os.path.join(root, file))
                
                if loose_count > 0 and os.path.exists(config['output_loose']):
                    for root, dirs, files in os.walk(config['output_loose']):
                        for file in files:
                            current_loose_files.append(os.path.join(root, file))
                
                if blacklisted_count > 0 and os.path.exists(config['output_blacklisted']):
                    for root, dirs, files in os.walk(config['output_blacklisted']):
                        for file in files:
                            current_blacklisted_files.append(os.path.join(root, file))
                
                self._handle_packaging(config, pack_count, loose_count, blacklisted_count, skip_count, 
                                     current_pack_files, current_loose_files, current_blacklisted_files)
        else:
            self.console.print("\n[yellow]⚠️ No files to process![/yellow]")
        
        input("\nPress Enter to continue...")

    def _execute_quick_start_processing_basic(self, config: Dict[str, Any]) -> None:
        """Execute Quick Start processing with basic UI."""
        from ..core import SafeResourcePacker
        from ..packaging.package_builder import PackageBuilder
        from ..config_cache import get_config_cache
        import os
        
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
            if input("\nProceed with packaging? [y/n] (y): ").strip().lower() not in ['n', 'no']:
                # Collect file lists from output directories
                current_pack_files = []
                current_loose_files = []
                current_blacklisted_files = []
                
                if pack_count > 0 and os.path.exists(config['output_pack']):
                    for root, dirs, files in os.walk(config['output_pack']):
                        for file in files:
                            current_pack_files.append(os.path.join(root, file))
                
                if loose_count > 0 and os.path.exists(config['output_loose']):
                    for root, dirs, files in os.walk(config['output_loose']):
                        for file in files:
                            current_loose_files.append(os.path.join(root, file))
                
                if blacklisted_count > 0 and os.path.exists(config['output_blacklisted']):
                    for root, dirs, files in os.walk(config['output_blacklisted']):
                        for file in files:
                            current_blacklisted_files.append(os.path.join(root, file))
                
                self._handle_packaging_basic(config, pack_count, loose_count, blacklisted_count, skip_count,
                                           current_pack_files, current_loose_files, current_blacklisted_files)
        else:
            print("\n⚠️ No files to process!")
        
        input("\nPress Enter to continue...")

    def _show_processing_header(self, config: Dict[str, Any]) -> None:
        """Show processing header with Rich UI."""
        from rich.panel import Panel
        
        header_panel = Panel.fit(
            f"🚀 [bold bright_white]Starting Processing[/bold bright_white]\n\n"
            f"📁 [bold cyan]Source:[/bold cyan] {config['source']}\n"
            f"🔧 [bold cyan]Generated:[/bold cyan] {config['generated']}\n"
            f"📦 [bold cyan]Pack Output:[/bold cyan] {config['output_pack']}\n"
            f"📁 [bold cyan]Loose Output:[/bold cyan] {config['output_loose']}\n"
            f"⚡ [bold cyan]Threads:[/bold cyan] {config.get('threads', 8)}\n"
            f"🐛 [bold cyan]Debug:[/bold cyan] {'Yes' if config.get('debug', False) else 'No'}",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()

    def _handle_packaging(self, config: Dict[str, Any], pack_count: int, loose_count: int, blacklisted_count: int, skip_count: int, pack_files: List[str] = None, loose_files: List[str] = None, blacklisted_files: List[str] = None):
        """Handle packaging with Rich UI."""
        from ..packaging.package_builder import PackageBuilder
        from ..dynamic_progress import log
        from rich.panel import Panel
        import os
        
        # Get mod name from generated directory
        mod_name = os.path.basename(config['generated'])
        esp_name = mod_name
        archive_name = mod_name
        
        # Determine package output directory
        package_output = os.path.dirname(config['output_pack'])
        
        # Validate package output directory
        is_valid, result = self._validate_directory_path(package_output, "package output directory")
        if not is_valid:
            # Try to create the directory
            try:
                os.makedirs(package_output, exist_ok=True)
                # Re-validate after creation
                is_valid, result = self._validate_directory_path(package_output, "package output directory")
                if is_valid:
                    package_output = result
                else:
                    # Use the original cleaned path, not the error message
                    package_output = package_output.strip().strip('"').strip("'")
                    self.console.print(f"[yellow]⚠️ Using original path: {package_output}[/yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Cannot create package directory: {e}[/red]")
                return
        
        # Show packaging start
        packaging_panel = Panel.fit(
            f"📦 [bold bright_white]Creating Complete Mod Package[/bold bright_white]\n\n"
            f"🎯 [bold cyan]Mod Name:[/bold cyan] {mod_name}\n"
            f"📄 [bold cyan]ESP Plugin:[/bold cyan] {esp_name}.esp\n"
            f"📦 [bold cyan]Archive:[/bold cyan] {archive_name}.bsa/.ba2\n"
            f"📁 [bold cyan]Output:[/bold cyan] {package_output}\n"
            f"🎮 [bold cyan]Game:[/bold cyan] {config.get('game_type', 'skyrim')}\n"
            f"⚡ [bold cyan]Compression:[/bold cyan] {config.get('compression', 3)}",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(packaging_panel)
        self.console.print()
        
        # Prepare classification results using the passed file lists
        classification_results = {}
        
        # Use the file lists passed from the classification process
        if pack_files:
            classification_results['pack'] = pack_files
            log(f"📦 Using {len(pack_files)} files for packing from current classification session", log_type='INFO')
        
        if loose_files:
            classification_results['loose'] = loose_files
            log(f"📁 Using {len(loose_files)} files for loose deployment from current classification session", log_type='INFO')
        
        if blacklisted_files:
            classification_results['blacklisted'] = blacklisted_files
            log(f"🚫 Using {len(blacklisted_files)} blacklisted files from current classification session", log_type='INFO')
        
        if not classification_results:
            self.console.print("[yellow]⚠️ No files to package[/yellow]")
            return
        
        # Set up packaging options
        options = {
            'cleanup_temp': True,
            'compression_level': config.get('compression', 3),
            'output_loose': config.get('output_loose'),      # Pass the user-defined loose folder
            'output_pack': config.get('output_pack'),        # Pass the user-defined pack folder
            'output_blacklisted': config.get('output_blacklisted'),  # Pass the user-defined blacklisted folder
            'source_root': config.get('source')             # Pass the source directory for blacklisted folders
        }
        
        # Initialize package builder
        package_builder = PackageBuilder(
            game_type=config.get('game_type', 'skyrim'),
            compression_level=config.get('compression', 3)
        )
        
        # Build complete package
        success, package_path, package_info = package_builder.build_complete_package(
            classification_results=classification_results,
            mod_name=mod_name,
            output_dir=package_output,
            options=options,
            esp_name=esp_name,
            archive_name=archive_name
        )
        
        if success:
            # Show success
            success_panel = Panel.fit(
                f"[bold green]✅ Package Creation Complete![/bold green]\n\n"
                f"📦 [bold cyan]Package:[/bold cyan] {package_path}\n"
                f"📄 [bold cyan]ESP:[/bold cyan] {esp_name}.esp\n"
                f"📦 [bold cyan]Archive:[/bold cyan] {archive_name}.bsa/.ba2",
                border_style="green",
                padding=(1, 2)
            )
            
            self.console.print(success_panel)
        else:
            self.console.print(f"[red]❌ Package creation failed: {package_info}[/red]")

    def _handle_packaging_basic(self, config: Dict[str, Any], pack_count: int, loose_count: int, blacklisted_count: int, skip_count: int, pack_files: List[str] = None, loose_files: List[str] = None, blacklisted_files: List[str] = None):
        """Handle packaging with basic UI."""
        from ..packaging.package_builder import PackageBuilder
        from ..dynamic_progress import log
        import os
        
        # Get mod name from generated directory
        mod_name = os.path.basename(config['generated'])
        esp_name = mod_name
        archive_name = mod_name
        
        # Determine package output directory
        package_output = os.path.dirname(config['output_pack'])
        
        # Validate package output directory
        is_valid, result = self._validate_directory_path(package_output, "package output directory")
        if not is_valid:
            # Try to create the directory
            try:
                os.makedirs(package_output, exist_ok=True)
                # Re-validate after creation
                is_valid, result = self._validate_directory_path(package_output, "package output directory")
                if is_valid:
                    package_output = result
                else:
                    # Use the original cleaned path, not the error message
                    package_output = package_output.strip().strip('"').strip("'")
                    print(f"⚠️ Using original path: {package_output}")
            except Exception as e:
                print(f"❌ Cannot create package directory: {e}")
                return
        
        print(f"\n📦 Starting Packaging Process")
        print(f"🎯 Mod Name: {mod_name}")
        print(f"📄 ESP: {esp_name}.esp")
        print(f"📦 Archive: {archive_name}.bsa/.ba2")
        
        # Prepare classification results using the passed file lists
        classification_results = {}
        
        # Use the file lists passed from the classification process
        if pack_files:
            classification_results['pack'] = pack_files
            log(f"📦 Using {len(pack_files)} files for packing from current classification session", log_type='INFO')
        
        if loose_files:
            classification_results['loose'] = loose_files
            log(f"📁 Using {len(loose_files)} files for loose deployment from current classification session", log_type='INFO')
        
        if blacklisted_files:
            classification_results['blacklisted'] = blacklisted_files
            log(f"🚫 Using {len(blacklisted_files)} blacklisted files from current classification session", log_type='INFO')
        
        if not classification_results:
            print("⚠️ No files to package")
            return
        
        # Set up packaging options
        options = {
            'cleanup_temp': True,
            'compression_level': config.get('compression', 3),
            'output_loose': config.get('output_loose'),      # Pass the user-defined loose folder
            'output_pack': config.get('output_pack'),        # Pass the user-defined pack folder
            'output_blacklisted': config.get('output_blacklisted'),  # Pass the user-defined blacklisted folder
            'source_root': config.get('source')             # Pass the source directory for blacklisted folders
        }
        
        # Initialize package builder
        package_builder = PackageBuilder(
            game_type=config.get('game_type', 'skyrim'),
            compression_level=config.get('compression', 3)
        )
        
        # Build complete package
        success, package_path, package_info = package_builder.build_complete_package(
            classification_results=classification_results,
            mod_name=mod_name,
            output_dir=package_output,
            options=options,
            esp_name=esp_name,
            archive_name=archive_name
        )
        
        if success:
            print(f"\n✅ Package Creation Complete!")
            print(f"📦 Package: {package_path}")
            print(f"📄 ESP: {esp_name}.esp")
            print(f"📦 Archive: {archive_name}.bsa/.ba2")
        else:
            print(f"\n❌ Package creation failed: {package_info}")
