"""
Simplified Console UI - Clean, minimal interactive interface

Provides a simple, user-friendly interface that runs on top of the CLI system.
Users can select options through menus instead of remembering command-line flags.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

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

    def _validate_directory_path(self, path: str, path_name: str) -> tuple[bool, str]:
        """
        Flexible and reliable directory path validation using existing logic.
        
        Args:
            path: The path to validate
            path_name: Human-readable name for error messages

        Returns:
            tuple: (is_valid, cleaned_path_or_error_message)
        """
        if not path:
            return False, f"{path_name} path cannot be empty"
        
        # Clean up the path (remove quotes, normalize)
        cleaned_path = path.strip().strip('"').strip("'")
        
        # Use existing validation utilities
        from .utils import validate_path_length
        
        # Check path length first (cross-platform compatibility)
        is_valid_length, length_error = validate_path_length(cleaned_path)
        if not is_valid_length:
            return False, f"{path_name} {length_error}"
        
        # Use the existing validation logic from enhanced_cli.py
        from pathlib import Path
        
        try:
            path_obj = Path(cleaned_path).expanduser().resolve()
        except (OSError, ValueError) as e:
            return False, f"Invalid path format: {cleaned_path} ({e})"
        
        if not path_obj.exists():
            # Check for common mistakes and suggest similar directories
            suggestions = []
            try:
                parent = path_obj.parent
                if parent.exists():
                    # Look for similar directories
                    similar = [d for d in parent.iterdir()
                              if d.is_dir() and d.name.lower().startswith(path_obj.name.lower()[:3])]
                    if similar:
                        suggestions.append(f"Did you mean: {', '.join(str(s) for s in similar[:3])}")
            except (OSError, PermissionError):
                pass  # Skip suggestions if we can't access parent
            
            suggestion_text = f" {suggestions[0]}" if suggestions else ""
            return False, f"{path_name} path does not exist: {cleaned_path}{suggestion_text}"
        
        if not path_obj.is_dir():
            if path_obj.is_file():
                return False, f"{path_name} path must be a directory (currently a file): {cleaned_path}"
            else:
                return False, f"{path_name} path is not accessible as a directory: {cleaned_path}"
        
        return True, str(path_obj)

    def _execute_processing(self, config: Dict[str, Any]):
        """Execute the actual processing with beautiful progress display."""
        if not RICH_AVAILABLE:
            self._execute_processing_basic(config)
            return

        try:
            # Import core functionality
            from .core import SafeResourcePacker
            from .dynamic_progress import enable_dynamic_progress, create_clean_progress_callback
            from .dynamic_progress import enhance_classifier_output
            
            # Enable dynamic progress
            enable_dynamic_progress(True)
            
            # Create packer
            packer = SafeResourcePacker(
                threads=config.get('threads', 8),
                debug=config.get('debug', False)
            )
            
            # Enhance classifier for beautiful output
            enhance_classifier_output(packer.classifier, quiet=False)
            
            # Show processing configuration
            config_panel = Panel.fit(
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

            self.console.print(config_panel)
            self.console.print()

            # Create progress callback
            progress_callback = create_clean_progress_callback(self.console, quiet=False)
                
            # Process resources with beautiful progress
            pack_count, loose_count, skip_count = packer.process_resources(
                config['source'], 
                config['generated'], 
                config['output_pack'], 
                config['output_loose'], 
                progress_callback
            )
            
            # Show classification results
            results_panel = Panel.fit(
                f"🎉 [bold bright_green]Classification Complete![/bold bright_green]\n\n"
                f"📦 [bold blue]Files to Pack:[/bold blue] {pack_count:,}\n"
                f"📁 [bold magenta]Files to Keep Loose:[/bold magenta] {loose_count:,}\n"
                f"⏭️ [bold yellow]Files Skipped:[/bold yellow] {skip_count:,}",
                border_style="bright_green",
                padding=(1, 2)
            )
            
            self.console.print()
            self.console.print(results_panel)
            self.console.print()
                
            # Ask if user wants to create package
            if pack_count > 0 or loose_count > 0:
                if Confirm.ask("Create complete mod package?", default=True):
                    # Store the current file lists immediately after classification
                    # This ensures we only get files from the current session
                    current_pack_files = []
                    current_loose_files = []
                    
                    if pack_count > 0 and os.path.exists(config['output_pack']):
                        for root, dirs, files in os.walk(config['output_pack']):
                            for file in files:
                                current_pack_files.append(os.path.join(root, file))
                        log(f"📦 Collected {len(current_pack_files)} pack files from output directory: {config['output_pack']}", log_type='INFO')
                        if len(current_pack_files) > 100:  # Log first few files if there are many
                            log(f"📦 First 5 pack files: {[os.path.basename(f) for f in current_pack_files[:5]]}", log_type='DEBUG')
                        else:
                            log(f"📦 All pack files: {[os.path.basename(f) for f in current_pack_files]}", log_type='DEBUG')
                    
                    if loose_count > 0 and os.path.exists(config['output_loose']):
                        for root, dirs, files in os.walk(config['output_loose']):
                            for file in files:
                                current_loose_files.append(os.path.join(root, file))
                        log(f"📁 Collected {len(current_loose_files)} loose files from output directory: {config['output_loose']}", log_type='INFO')
                        if len(current_loose_files) > 100:  # Log first few files if there are many
                            log(f"📁 First 5 loose files: {[os.path.basename(f) for f in current_loose_files[:5]]}", log_type='DEBUG')
                        else:
                            log(f"📁 All loose files: {[os.path.basename(f) for f in current_loose_files]}", log_type='DEBUG')
                    
                    # Check if pack and loose directories are the same (this should not happen with validation)
                    if (os.path.normpath(os.path.abspath(config['output_pack'])) == 
                        os.path.normpath(os.path.abspath(config['output_loose']))):
                        log(f"⚠️ WARNING: Pack and loose directories are the same! This will cause file duplication.", log_type='WARNING')
                        log(f"   Pack: {config['output_pack']}", log_type='WARNING')
                        log(f"   Loose: {config['output_loose']}", log_type='WARNING')
                    
                    self._handle_packaging(config, pack_count, loose_count, skip_count, current_pack_files, current_loose_files)
            else:
                self.console.print("[yellow]⚠️ No files to package[/yellow]")
            
            # Save configuration to cache after successful processing
            from .config_cache import get_config_cache
            config_cache = get_config_cache()
            config_cache.save_config(config)
            
            # Ask if user wants to continue
            if not Confirm.ask("Continue to main menu?", default=True):
                return
                
        except Exception as e:
            self.console.print(f"[red]❌ Processing failed: {e}[/red]")
            self.console.print()
            if not Confirm.ask("Continue to main menu?", default=True):
                return

    def _execute_processing_basic(self, config: Dict[str, Any]):
        """Execute processing in basic mode (no Rich)."""
        try:
            from .core import SafeResourcePacker
            
            print("\n🚀 Starting Processing...")
            print(f"📁 Source: {config['source']}")
            print(f"🔧 Generated: {config['generated']}")
            print(f"📦 Pack Output: {config['output_pack']}")
            print(f"📁 Loose Output: {config['output_loose']}")
            print()
            
            # Create packer
            packer = SafeResourcePacker(
                threads=config.get('threads', 8),
                debug=config.get('debug', False)
            )
            
            # Process resources
            pack_count, loose_count, skip_count = packer.process_resources(
                config['source'], 
                config['generated'], 
                config['output_pack'], 
                config['output_loose']
            )
            
            print(f"\n🎉 Processing Complete!")
            print(f"📦 Files to Pack: {pack_count:,}")
            print(f"📁 Files to Keep Loose: {loose_count:,}")
            print(f"⏭️ Files Skipped: {skip_count:,}")
            print()
            
            # Save configuration to cache after successful processing
            from .config_cache import get_config_cache
            config_cache = get_config_cache()
            config_cache.save_config(config)
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            print()

    def _handle_packaging(self, config: Dict[str, Any], pack_count: int, loose_count: int, skip_count: int, pack_files: List[str] = None, loose_files: List[str] = None):
        """Handle the complete packaging process."""
        try:
            # Get mod name from user
            mod_name = Prompt.ask(
                "[bold cyan]📝 Mod name for package[/bold cyan]",
                default=os.path.basename(os.path.normpath(config['generated']))
            )
            
            # Get ESP plugin name from user
            esp_name = Prompt.ask(
                "[bold cyan]📄 ESP plugin name[/bold cyan]",
                default=mod_name
            )
            
            # Get archive name from user
            archive_name = Prompt.ask(
                "[bold cyan]📦 Archive name[/bold cyan]",
                default=mod_name
            )
            
            # Get output directory for package
            package_output = Prompt.ask(
                "[bold cyan]📁 Package output directory[/bold cyan]",
                default=os.path.join(os.path.dirname(config['output_pack']), f"{mod_name}_Package")
            )
            
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
                f"⚡ [bold cyan]Compression:[/bold cyan] {config.get('compression', 5)}",
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
            
            if not classification_results:
                self.console.print("[yellow]⚠️ No files to package[/yellow]")
                return
            
            # Set up packaging options
            options = {
                'cleanup_temp': True,
                'compression_level': config.get('compression', 5),
                'output_loose': config.get('output_loose'),  # Pass the user-defined loose folder
                'output_pack': config.get('output_pack')    # Pass the user-defined pack folder
            }
            
            # Initialize package builder
            from .packaging import PackageBuilder
            
            package_builder = PackageBuilder(
                game_type=config.get('game_type', 'skyrim'),
                compression_level=config.get('compression', 5)
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
                    f"✨ [bold bright_green]Package Created Successfully![/bold bright_green]\n\n"
                    f"📦 [bold cyan]Package Path:[/bold cyan] {package_path}\n"
                    f"🎯 [bold cyan]Mod Name:[/bold cyan] {mod_name}\n"
                    f"📊 [bold cyan]Components:[/bold cyan] {len(package_info.get('components', {}))}",
                    border_style="bright_green",
                    padding=(1, 2)
                )
                
                self.console.print()
                self.console.print(success_panel)
                self.console.print()
                
                # Show package contents
                if 'components' in package_info:
                    self.console.print("[bold cyan]📋 Package Contents:[/bold cyan]")
                    for comp_name, comp_info in package_info['components'].items():
                        if isinstance(comp_info, dict) and 'path' in comp_info:
                            file_name = os.path.basename(comp_info['path'])
                            self.console.print(f"  📄 {file_name}")
                
            else:
                self.console.print(f"[red]❌ Package creation failed: {package_path}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Packaging failed: {e}[/red]")
            self.console.print()

    def _execute_batch_repacking(self, config: Dict[str, Any]):
        """Execute batch repacking with progress display."""
        if not RICH_AVAILABLE:
            self._execute_batch_repacking_basic(config)
            return

        try:
            from .batch_repacker import BatchModRepacker
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            
            # Show configuration
            config_panel = Panel.fit(
                f"📦 [bold bright_white]Batch Mod Repacking[/bold bright_white]\n\n"
                f"📁 [bold cyan]Collection:[/bold cyan] {config['collection']}\n"
                f"🎮 [bold cyan]Game:[/bold cyan] {config['game_type']}\n"
                f"⚡ [bold cyan]Threads:[/bold cyan] {config.get('threads', 8)}",
                border_style="bright_green",
                padding=(1, 2)
            )
            
            self.console.print(config_panel)
            self.console.print()
            
            # Initialize batch repacker
            batch_repacker = BatchModRepacker(
                game_type=config.get('game_type', 'skyrim'),
                threads=config.get('threads', 8)
            )
            
            # Discover mods in collection
            all_mods = batch_repacker.discover_mods(config['collection'])
            if not all_mods:
                self.console.print("[red]❌ No mods found in collection path![/red]")
                return
            
            # Check BSArch availability (force refresh to clear invalid cache)
            bsarch_available, bsarch_message = batch_repacker.check_bsarch_availability(force_refresh=True)
            if bsarch_available:
                self.console.print(f"[green]✅ {bsarch_message}[/green]")
            else:
                self.console.print(f"[yellow]⚠️ {bsarch_message}[/yellow]")
            self.console.print()
            
            # Show discovery summary
            self.console.print("[bold blue]📋 Discovery Results:[/bold blue]")
            self.console.print(batch_repacker.get_discovery_summary())
            self.console.print()
            
            # Handle plugin selection for mods with multiple plugins
            mods_needing_selection = [mod for mod in all_mods if not mod.esp_file and mod.available_plugins]
            if mods_needing_selection:
                self.console.print("[bold yellow]🔧 Plugin Selection Required:[/bold yellow]")
                for mod_info in mods_needing_selection:
                    self._select_plugin_for_mod(mod_info)
                self.console.print()
            
            # Multi-select mods to process
            selected_mods = self._select_mods_to_process(all_mods)
            if not selected_mods:
                self.console.print("[red]❌ No mods selected for processing![/red]")
                return
            batch_repacker.discovered_mods = selected_mods
            
            # Progress tracking
            def progress_callback(current, total, message):
                self.console.print(f"[cyan]📦 [{current+1}/{total}][/cyan] {message}")
            
            # Execute batch processing with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                
                task = progress.add_task("Batch repacking mods...", total=100)
                
                def progress_wrapper_with_bar(current, total, message):
                    progress.update(task, completed=current, description=f"Processing: {message}")
                    progress_callback(current, total, message)
                
                results = batch_repacker.process_mod_collection(
                    collection_path=config['collection'],
                    output_path=config.get('output_path', config['collection'] + '_repacked'),
                    progress_callback=progress_wrapper_with_bar
                )
            
            # Display results
            if results['success']:
                self.console.print(f"[green]🎉 Batch processing completed![/green]")
                self.console.print(f"[green]✅ Processed: {results['processed']} mods[/green]")
                if results['failed'] > 0:
                    self.console.print(f"[yellow]❌ Failed: {results['failed']} mods[/yellow]")
                self.console.print()
                self.console.print(batch_repacker.get_summary_report())
            else:
                self.console.print(f"[red]❌ Batch processing failed: {results['message']}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Batch repacking failed: {e}[/red]")
            import traceback
            self.console.print(f"[red]Error details: {traceback.format_exc()}[/red]")
            self.console.print()

    def _execute_batch_repacking_basic(self, config: Dict[str, Any]):
        """Execute batch repacking in basic mode."""
        print("\n📦 Batch Mod Repacking")
        print(f"📁 Collection: {config['collection']}")
        print(f"🎮 Game: {config['game_type']}")
        print(f"⚡ Threads: {config.get('threads', 8)}")
        print()
        
        try:
            from .batch_repacker import BatchModRepacker
            batch_repacker = BatchModRepacker(
                game_type=config.get('game_type', 'skyrim'),
                threads=config.get('threads', 8)
            )
            
            # Discover mods in collection
            all_mods = batch_repacker.discover_mods(config['collection'])
            if not all_mods:
                print("❌ No mods found in collection path!")
                return
            
            # Check BSArch availability
            bsarch_available, bsarch_message = batch_repacker.check_bsarch_availability()
            if bsarch_available:
                print(f"✅ {bsarch_message}")
            else:
                print(f"⚠️ {bsarch_message}")
            print()
            
            # Show discovery summary
            print("📋 Discovery Results:")
            print(batch_repacker.get_discovery_summary())
            print()
            
            # Handle plugin selection for mods with multiple plugins
            mods_needing_selection = [mod for mod in all_mods if not mod.esp_file and mod.available_plugins]
            if mods_needing_selection:
                print("🔧 Plugin Selection Required:")
                for mod_info in mods_needing_selection:
                    self._select_plugin_for_mod_basic(mod_info)
                print()
            
            # Multi-select mods to process
            selected_mods = self._select_mods_to_process_basic(all_mods)
            if not selected_mods:
                print("❌ No mods selected for processing!")
                return
            batch_repacker.discovered_mods = selected_mods
            
            def simple_progress(current, total, message):
                print(f"📦 [{current+1}/{total}] {message}")
            
            # Execute batch processing
            results = batch_repacker.process_mod_collection(
                collection_path=config['collection'],
                output_path=config.get('output_path', config['collection'] + '_repacked'),
                progress_callback=simple_progress
            )
            
            # Display results
            if results['success']:
                print(f"🎉 Batch processing completed!")
                print(f"✅ Processed: {results['processed']} mods")
                if results['failed'] > 0:
                    print(f"❌ Failed: {results['failed']} mods")
                print()
                print(batch_repacker.get_summary_report())
            else:
                print(f"❌ Batch processing failed: {results['message']}")
                
        except Exception as e:
            print(f"❌ Batch repacking failed: {e}")
            import traceback
            traceback.print_exc()

    def _select_plugin_for_mod(self, mod_info):
        """Let user select which plugin to use for a mod with multiple plugins."""
        self.console.print(f"[bold cyan]📋 {mod_info.mod_name}[/bold cyan]")
        self.console.print(f"   Found {len(mod_info.available_plugins)} plugins:")
        
        for i, (plugin_path, plugin_type) in enumerate(mod_info.available_plugins):
            plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
            self.console.print(f"   {i+1}. {plugin_name}.{plugin_type.lower()}")
        
        while True:
            try:
                choice = self.console.input(f"   Select plugin (1-{len(mod_info.available_plugins)}) or 'a' for auto-select: ").strip()
                
                if choice.lower() == 'a':
                    # Auto-select first plugin
                    from .batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, 0)
                    self.console.print(f"   [green]✅ Auto-selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}[/green]")
                    break
                
                plugin_index = int(choice) - 1
                if 0 <= plugin_index < len(mod_info.available_plugins):
                    from .batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, plugin_index)
                    self.console.print(f"   [green]✅ Selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}[/green]")
                    break
                else:
                    self.console.print(f"   [red]❌ Invalid choice. Please enter 1-{len(mod_info.available_plugins)} or 'a'[/red]")
            except ValueError:
                self.console.print(f"   [red]❌ Invalid input. Please enter a number or 'a'[/red]")

    def _select_mods_to_process(self, all_mods):
        """Let user select which mods to process (multi-select)."""
        self.console.print("[bold yellow]🎯 Mod Selection:[/bold yellow]")
        self.console.print("Select which mods to process (you can select multiple):")
        self.console.print()
        
        for i, mod_info in enumerate(all_mods, 1):
            plugin_info = f"{mod_info.esp_name}.{mod_info.esp_type.lower()}" if mod_info.esp_file else f"{len(mod_info.available_plugins)} plugins"
            self.console.print(f"   {i}. {mod_info.mod_name} ({plugin_info})")
        
        self.console.print()
        self.console.print("Options:")
        self.console.print("   • Enter numbers separated by commas (e.g., 1,3,5)")
        self.console.print("   • Enter 'a' to select all mods")
        self.console.print("   • Enter 'q' to quit")
        
        while True:
            try:
                choice = self.console.input("   Your selection: ").strip()
                
                if choice.lower() == 'q':
                    return []
                
                if choice.lower() == 'a':
                    self.console.print(f"   [green]✅ Selected all {len(all_mods)} mods[/green]")
                    return all_mods
                
                # Parse comma-separated numbers
                selected_indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(all_mods):
                            selected_indices.append(idx)
                        else:
                            self.console.print(f"   [red]❌ Invalid number: {part} (must be 1-{len(all_mods)})[/red]")
                            break
                    else:
                        self.console.print(f"   [red]❌ Invalid input: {part} (must be numbers)[/red]")
                        break
                else:
                    # All numbers were valid
                    if selected_indices:
                        selected_mods = [all_mods[i] for i in selected_indices]
                        self.console.print(f"   [green]✅ Selected {len(selected_mods)} mods:[/green]")
                        for mod_info in selected_mods:
                            self.console.print(f"      • {mod_info.mod_name}")
                        return selected_mods
                    else:
                        self.console.print(f"   [red]❌ No valid selections made[/red]")
                        
            except Exception as e:
                self.console.print(f"   [red]❌ Error: {e}[/red]")

    def _select_plugin_for_mod_basic(self, mod_info):
        """Let user select which plugin to use for a mod with multiple plugins (basic UI)."""
        print(f"📋 {mod_info.mod_name}")
        print(f"   Found {len(mod_info.available_plugins)} plugins:")
        
        for i, (plugin_path, plugin_type) in enumerate(mod_info.available_plugins):
            plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
            print(f"   {i+1}. {plugin_name}.{plugin_type.lower()}")
        
        while True:
            try:
                choice = input(f"   Select plugin (1-{len(mod_info.available_plugins)}) or 'a' for auto-select: ").strip()
                
                if choice.lower() == 'a':
                    # Auto-select first plugin
                    from .batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, 0)
                    print(f"   ✅ Auto-selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}")
                    break
                
                plugin_index = int(choice) - 1
                if 0 <= plugin_index < len(mod_info.available_plugins):
                    from .batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, plugin_index)
                    print(f"   ✅ Selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}")
                    break
                else:
                    print(f"   ❌ Invalid choice. Please enter 1-{len(mod_info.available_plugins)} or 'a'")
            except ValueError:
                print(f"   ❌ Invalid input. Please enter a number or 'a'")

    def _select_mods_to_process_basic(self, all_mods):
        """Let user select which mods to process (multi-select, basic UI)."""
        print("🎯 Mod Selection:")
        print("Select which mods to process (you can select multiple):")
        print()
        
        for i, mod_info in enumerate(all_mods, 1):
            plugin_info = f"{mod_info.esp_name}.{mod_info.esp_type.lower()}" if mod_info.esp_file else f"{len(mod_info.available_plugins)} plugins"
            print(f"   {i}. {mod_info.mod_name} ({plugin_info})")
        
        print()
        print("Options:")
        print("   • Enter numbers separated by commas (e.g., 1,3,5)")
        print("   • Enter 'a' to select all mods")
        print("   • Enter 'q' to quit")
        
        while True:
            try:
                choice = input("   Your selection: ").strip()
                
                if choice.lower() == 'q':
                    return []
                
                if choice.lower() == 'a':
                    print(f"   ✅ Selected all {len(all_mods)} mods")
                    return all_mods
                
                # Parse comma-separated numbers
                selected_indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(all_mods):
                            selected_indices.append(idx)
                        else:
                            print(f"   ❌ Invalid number: {part} (must be 1-{len(all_mods)})")
                            break
                    else:
                        print(f"   ❌ Invalid input: {part} (must be numbers)")
                        break
                else:
                    # All numbers were valid
                    if selected_indices:
                        selected_mods = [all_mods[i] for i in selected_indices]
                        print(f"   ✅ Selected {len(selected_mods)} mods:")
                        for mod_info in selected_mods:
                            print(f"      • {mod_info.mod_name}")
                        return selected_mods
                    else:
                        print(f"   ❌ No valid selections made")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")

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
                    try:
                        config = self._quick_start_wizard()
                        if config:
                            self._execute_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Quick start wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
                elif choice == "2":
                    # Advanced Classification
                    try:
                        config = self._advanced_classification_wizard()
                        if config:
                            self._execute_processing(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Advanced classification wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
                elif choice == "3":
                    # Batch Mod Repacking
                    try:
                        config = self._batch_repacking_wizard()
                        if config:
                            self._execute_batch_repacking(config)
                    except Exception as e:
                        self.console.print(f"[red]❌ Batch repacking wizard failed: {e}[/red]")
                        self.console.print("[yellow]Returning to main menu...[/yellow]")
                        self.console.print()
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

        # Beautiful welcome banner
        welcome_panel = Panel.fit(
            "[bold bright_white]🎮 Safe Resource Packer[/bold bright_white]\n"
            "[bold bright_cyan]Professional Mod File Classification & Packaging[/bold bright_cyan]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()

        # Feature highlights with icons
        features_text = """
[bold bright_green]✨ What this tool does:[/bold bright_green]

[bold green]🔍 Smart Classification[/bold green]     [dim]→ Analyzes mod files and classifies them intelligently[/dim]
[bold green]📦 Archive Creation[/bold green]        [dim]→ Creates optimized BSA/BA2 archives for safe files[/dim]
[bold green]🔄 Override Protection[/bold green]     [dim]→ Keeps override files loose to prevent conflicts[/dim]
[bold green]🎯 Game Support[/bold green]            [dim]→ Perfect for Skyrim, Fallout 4, and Creation Engine games[/dim]
[bold green]⚡ Batch Processing[/bold green]        [dim]→ Process multiple mods efficiently[/dim]
[bold green]🛠️ Easy Setup[/bold green]             [dim]→ Simple wizards and automated tool installation[/dim]
        """

        self.console.print(features_text)
        self.console.print()
        
        # Quick start tip
        tip_panel = Panel(
            "[bold yellow]💡 Quick Start Tip:[/bold yellow] Choose 'Quick Start' for most users, or 'Advanced' for custom setups",
            border_style="yellow",
            padding=(1, 1)
        )
        
        self.console.print(tip_panel)
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

        # Create beautiful main menu with hints and examples
        menu_panel = Panel.fit(
            "[bold bright_white]🎮 Safe Resource Packer[/bold bright_white]\n"
            "[dim]Professional mod file packaging and classification[/dim]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        self.console.print()
        
        # Main menu options with detailed descriptions
        menu_text = """
[bold cyan]📋 Main Menu[/bold cyan]

[bold green]1.[/bold green] [bold]Quick Start (Packaging)[/bold]     [dim]→ Classify and package mod files automatically[/dim]
[bold green]2.[/bold green] [bold]Advanced Classification[/bold]     [dim]→ Fine-tune classification rules and settings[/dim]
[bold green]3.[/bold green] [bold]Batch Mod Repacking[/bold]        [dim]→ Process multiple mods in sequence[/dim]
[bold green]4.[/bold green] [bold]Tools & Setup[/bold]              [dim]→ Install BSArch, check system requirements[/dim]
[bold green]5.[/bold green] [bold]Help & Info[/bold]                [dim]→ Documentation, examples, and troubleshooting[/dim]
[bold green]6.[/bold green] [bold]Exit[/bold]                       [dim]→ Close the application[/dim]

[dim]💡 Tip: Start with Quick Start for most users, or Advanced for custom setups[/dim]
        """
        
        self.console.print(menu_text)
        self.console.print()
        
        return Prompt.ask(
            "[bold bright_cyan]Choose an option[/bold bright_cyan]",
            choices=["1", "2", "3", "4", "5", "6", "q"],
            default="1"
        )

    def _quick_start_wizard(self) -> Optional[Dict[str, Any]]:
        """Quick start wizard for packaging."""
        if not RICH_AVAILABLE:
            return self._basic_quick_start()

        # Check for cached configuration
        from .config_cache import get_config_cache
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
        
        # Validate that pack and loose directories are different
        if os.path.normpath(os.path.abspath(output_pack)) == os.path.normpath(os.path.abspath(output_loose)):
            self.console.print("[red]❌ Pack and loose output directories cannot be the same![/red]")
            self.console.print(f"[red]   Pack: {output_pack}[/red]")
            self.console.print(f"[red]   Loose: {output_loose}[/red]")
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
        """Basic quick start for when Rich is not available."""
        print("\n🚀 Quick Start - File Packaging")
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

        return config

    def _batch_repacking_wizard(self) -> Optional[Dict[str, Any]]:
        """Batch repacking wizard."""
        if not RICH_AVAILABLE:
            return self._basic_batch_repacking()

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

        config['collection'] = input("Collection directory (💡 Tip: You can drag and drop a folder here): ").strip()
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
        
        is_valid, result = self._validate_directory_path(source, "source directory")
        if not is_valid:
            self.console.print(f"[red]❌ {result}[/red]")
            return None
        source = result

        # Get generated directory
        generated = Prompt.ask(
            "[bold cyan]📂 Generated files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
            default=""
        )
        
        is_valid, result = self._validate_directory_path(generated, "generated directory")
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

        # Beautiful system check header
        header_panel = Panel.fit(
            "[bold bright_blue]🔍 System Setup Check[/bold bright_blue]\n"
            "[dim]Checking system requirements and setup...[/dim]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()

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

        # Beautiful completion message
        completion_panel = Panel.fit(
            "[bold bright_green]✅ System check completed![/bold bright_green]",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(completion_panel)

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
