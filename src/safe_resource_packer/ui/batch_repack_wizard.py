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

from ..config_service import ConfigService


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
        # Use centralized configuration service
        config_service = ConfigService(self.console)
        return config_service.collect_batch_repack_config(use_cached=True)

    def _basic_batch_repacking(self) -> Optional[Dict[str, Any]]:
        """Basic Batch Repacking for when Rich is not available."""
        # Use centralized configuration service
        config_service = ConfigService(None)  # No console for basic mode
        return config_service.collect_batch_repack_config(use_cached=True)

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
        """Execute batch repacking processing with Rich UI."""
        if not RICH_AVAILABLE:
            self._execute_batch_repack_processing_basic(config)
            return

        try:
            from ..batch_repacker import BatchModRepacker
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
            
            # Check BSArch availability (only force refresh if there's an error)
            bsarch_available, bsarch_message = batch_repacker.check_bsarch_availability(force_refresh=False)
            if bsarch_available:
                self.console.print(f"[green]✅ {bsarch_message}[/green]")
            else:
                # If BSArch is not available, try with force refresh to clear invalid cache
                self.console.print(f"[yellow]⚠️ {bsarch_message}[/yellow]")
                self.console.print("[blue]🔄 Attempting to refresh BSArch detection...[/blue]")
                bsarch_available, bsarch_message = batch_repacker.check_bsarch_availability(force_refresh=True)
                if bsarch_available:
                    self.console.print(f"[green]✅ {bsarch_message}[/green]")
                else:
                    self.console.print(f"[red]❌ {bsarch_message}[/red]")
            self.console.print()
            
            # Show discovery summary
            self.console.print("[bold blue]📋 Discovery Results:[/bold blue]")
            self.console.print(batch_repacker.get_discovery_summary())
            self.console.print()
            
            # Step 1: Multi-select mods to process FIRST
            selected_mods = self._select_mods_to_process(all_mods)
            if not selected_mods:
                self.console.print("[red]❌ No mods selected for processing![/red]")
                return
            
            # Step 2: Handle plugin selection for selected mods with multiple plugins
            mods_needing_selection = [mod for mod in selected_mods if not mod.esp_file and mod.available_plugins]
            if mods_needing_selection:
                self.console.print("[bold yellow]🔧 Plugin Selection Required:[/bold yellow]")
                for mod_info in mods_needing_selection:
                    self._select_plugin_for_mod(mod_info)
                self.console.print()
            
            # Step 3: Handle folder selection for selected mods with multiple asset folders
            mods_needing_folder_selection = [mod for mod in selected_mods if mod.available_folders and len(mod.available_folders) > 1]
            if mods_needing_folder_selection:
                self.console.print("[bold yellow]📁 Folder Selection Required:[/bold yellow]")
                for mod_info in mods_needing_folder_selection:
                    self._select_folders_for_mod(mod_info)
                self.console.print()
            
            # Set the selected mods with all their selections
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

    def _execute_batch_repack_processing_basic(self, config: Dict[str, Any]) -> None:
        """Execute batch repack processing in basic mode."""
        print("\n📦 Batch Mod Repacking")
        print(f"📁 Collection: {config['collection']}")
        print(f"🎮 Game: {config['game_type']}")
        print(f"⚡ Threads: {config.get('threads', 8)}")
        print()
        
        try:
            from ..batch_repacker import BatchModRepacker
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
                    from ..batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, 0)
                    self.console.print(f"   [green]✅ Auto-selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}[/green]")
                    break
                
                plugin_index = int(choice) - 1
                if 0 <= plugin_index < len(mod_info.available_plugins):
                    from ..batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, plugin_index)
                    self.console.print(f"   [green]✅ Selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}[/green]")
                    break
                else:
                    self.console.print(f"   [red]❌ Invalid choice. Please enter 1-{len(mod_info.available_plugins)} or 'a'[/red]")
            except ValueError:
                self.console.print(f"   [red]❌ Invalid input. Please enter a number or 'a'[/red]")

    def _select_folders_for_mod(self, mod_info):
        """Let user select which asset folders to pack for a mod."""
        from ..constants import is_unpackable_folder, get_unpackable_folders_from_list
        
        self.console.print(f"[bold cyan]📁 {mod_info.mod_name}[/bold cyan]")
        
        # Separate packable and unpackable folders
        folder_names = [os.path.basename(folder) for folder in mod_info.available_folders]
        unpackable_folders = get_unpackable_folders_from_list(folder_names, mod_info.game_type)
        packable_folders = [folder for folder in mod_info.available_folders 
                           if os.path.basename(folder) not in unpackable_folders]
        
        if unpackable_folders:
            self.console.print(f"   [yellow]📦 Unpackable folders (will stay loose):[/yellow]")
            for folder in unpackable_folders:
                self.console.print(f"      • {folder} [dim](blacklisted)[/dim]")
            self.console.print()
        
        if len(packable_folders) <= 1:
            # Only one packable folder or none, auto-select
            if packable_folders:
                mod_info.selected_folders = packable_folders
                self.console.print(f"   [green]✅ Auto-selected: {os.path.basename(packable_folders[0])}[/green]")
            else:
                mod_info.selected_folders = []
                self.console.print("   [yellow]⚠️ No packable folders found[/yellow]")
            return
        
        self.console.print(f"   [yellow]Found {len(packable_folders)} packable folders:[/yellow]")
        for i, folder in enumerate(packable_folders, 1):
            folder_name = os.path.basename(folder)
            self.console.print(f"      {i}. {folder_name}")
        
        self.console.print(f"      {len(packable_folders) + 1}. All folders")
        
        while True:
            try:
                choice = self.console.input(f"   Select folders (1-{len(packable_folders) + 1}) or 'a' for all: ").strip()
                
                if choice.lower() in ['a', 'all']:
                    mod_info.selected_folders = packable_folders
                    self.console.print(f"   [green]✅ Selected all {len(packable_folders)} folders[/green]")
                    break
                else:
                    # Parse comma-separated choices
                    choices = [c.strip() for c in choice.split(',')]
                    selected_folders = []
                    
                    for choice_str in choices:
                        try:
                            choice_idx = int(choice_str) - 1
                            if 0 <= choice_idx < len(packable_folders):
                                selected_folders.append(packable_folders[choice_idx])
                            elif choice_idx == len(packable_folders):
                                # "All folders" option selected
                                selected_folders = packable_folders.copy()
                                break
                            else:
                                self.console.print(f"   [red]❌ Invalid choice: {choice_str}[/red]")
                                break
                        except ValueError:
                            self.console.print(f"   [red]❌ Invalid choice: {choice_str}[/red]")
                            break
                    else:
                        # All choices were valid
                        mod_info.selected_folders = selected_folders
                        selected_names = [os.path.basename(f) for f in selected_folders]
                        self.console.print(f"   [green]✅ Selected: {', '.join(selected_names)}[/green]")
                        break
                        
            except KeyboardInterrupt:
                self.console.print("\n   [yellow]⚠️ Selection cancelled[/yellow]")
                return

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
                    from ..batch_repacker import BatchModRepacker
                    batch_repacker = BatchModRepacker()
                    batch_repacker.select_plugin_for_mod(mod_info, 0)
                    print(f"   ✅ Auto-selected: {mod_info.esp_name}.{mod_info.esp_type.lower()}")
                    break
                
                plugin_index = int(choice) - 1
                if 0 <= plugin_index < len(mod_info.available_plugins):
                    from ..batch_repacker import BatchModRepacker
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
