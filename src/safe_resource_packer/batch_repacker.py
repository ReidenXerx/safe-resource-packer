"""
Batch Mod Repacker - Automatically repack collections of mods

This module provides functionality to automatically process entire folders of mods,
where each mod has its own ESP/ESL/ESM file and loose assets, converting them into
optimized BSA/BA2 + ESP packages ready for distribution.

Naming Conventions:
- Functions with 'batch_repack_' prefix: Used for Batch Repacking mode (multiple mods processing)
- Functions without prefix: Shared utilities used by batch processing

Expected folder structure:
ModCollection/
├── ModA/
│   ├── ModA.esp
│   ├── meshes/
│   ├── textures/
│   └── ...
├── ModB/
│   ├── ModB.esm
│   ├── scripts/
│   └── ...
└── ModC/
    ├── ModC.esl
    └── sounds/
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from .dynamic_progress import log
from .utils import safe_walk, sanitize_filename, check_disk_space, format_bytes
from .core import SafeResourcePacker
from .packaging import PackageBuilder
from .constants import is_unpackable_folder, get_packable_folders, get_unpackable_folders_from_list


class ModInfo:
    """Information about a discovered mod."""
    
    def __init__(self, mod_path: str, esp_file: str = None, esp_type: str = None, game_type: str = "skyrim"):
        self.mod_path = mod_path
        self.mod_name = os.path.basename(mod_path)
        self.esp_file = esp_file
        self.esp_name = os.path.splitext(os.path.basename(esp_file))[0] if esp_file else None
        self.esp_type = esp_type.upper() if esp_type else None  # ESP, ESL, ESM
        self.game_type = game_type.lower()  # skyrim, fallout4, etc.
        self.asset_files = []
        self.asset_size = 0
        self.asset_categories = set()  # Categories of assets found
        self.available_plugins = []  # List of (path, type) tuples for multiple plugins
        self.available_folders = []  # List of asset folders found
        
    def __repr__(self):
        if self.esp_file:
            return f"ModInfo({self.mod_name}, {self.esp_type}, {len(self.asset_files)} assets)"
        else:
            return f"ModInfo({self.mod_name}, {len(self.available_plugins)} plugins, {len(self.available_folders)} folders)"


class BatchModRepacker:
    """Handles batch repacking of mod collections."""
    
    def __init__(self, game_type: str = "skyrim", threads: int = 8, config: Optional[Dict] = None):
        """
        Initialize batch repacker.
        
        Args:
            game_type: Target game ("skyrim" or "fallout4")
            threads: Number of threads for processing
            config: Optional configuration dictionary for customization
        """
        self.game_type = game_type.lower()
        self.threads = threads
        self.discovered_mods = []
        self.processed_mods = []
        self.failed_mods = []
        
        # Load configuration with flexible defaults
        self.config = self._load_config(config or {})
    
    def _load_config(self, user_config: Dict) -> Dict:
        """
        Simple configuration for batch repacking - just pack everything.
        
        Args:
            user_config: User-provided configuration overrides
            
        Returns:
            Complete configuration dictionary
        """
        # Simple config - we just pack whatever assets we find
        default_config = {
            # Plugin file extensions 
            'plugin_extensions': ['.esp', '.esl', '.esm'],
            
            # Package naming
            'package_naming': {
                'use_esp_name': True,
                'suffix': '',  # Clean naming
                'version': 'v1.0',
                'separator': '_'
            },
            
            # Processing options
            'processing': {
                'max_depth': 10,
                'min_assets': 1,
                'skip_hidden': True
            }
        }
        
        # Merge user config with defaults
        merged_config = default_config.copy()
        for key, value in user_config.items():
            if isinstance(value, dict) and key in merged_config:
                merged_config[key].update(value)
            else:
                merged_config[key] = value
        
        return merged_config
    
    def select_plugin_for_mod(self, mod_info: ModInfo, plugin_index: int = None) -> bool:
        """
        Select which plugin to use for a mod that has multiple plugins.
        
        Args:
            mod_info: ModInfo object with multiple plugins
            plugin_index: Index of plugin to select (0-based), or None for auto-select
            
        Returns:
            True if selection successful, False otherwise
        """
        if not mod_info.available_plugins:
            return False
        
        if plugin_index is None:
            # Auto-select first plugin
            plugin_index = 0
        
        if 0 <= plugin_index < len(mod_info.available_plugins):
            plugin_path, plugin_type = mod_info.available_plugins[plugin_index]
            mod_info.esp_file = plugin_path
            mod_info.esp_name = os.path.splitext(os.path.basename(plugin_path))[0]
            mod_info.esp_type = plugin_type
            return True
        
        return False
    
    def select_folders_for_mod(self, mod_info: ModInfo, selected_folders: List[str] = None) -> bool:
        """
        Select which asset folders to pack for a mod.
        
        Args:
            mod_info: ModInfo object with available folders
            selected_folders: List of folder paths to pack, or None for all folders
            
        Returns:
            True if selection successful, False otherwise
        """
        if not mod_info.available_folders:
            return True  # No folders to select, use all assets
        
        if selected_folders is None:
            # Auto-select all folders
            selected_folders = mod_info.available_folders
        
        # Filter asset files to only include those from selected folders
        filtered_assets = []
        total_size = 0
        
        for asset_file in mod_info.asset_files:
            # Check if this asset file is in any of the selected folders
            asset_dir = os.path.dirname(asset_file)
            if any(asset_dir.startswith(folder) for folder in selected_folders):
                filtered_assets.append(asset_file)
                try:
                    total_size += os.path.getsize(asset_file)
                except OSError:
                    pass
        
        mod_info.asset_files = filtered_assets
        mod_info.asset_size = total_size
        return True
    
    def get_discovery_summary(self) -> str:
        """
        Get a summary of discovered mods with their plugin and folder information.
        
        Returns:
            Formatted string with discovery summary
        """
        if not self.discovered_mods:
            return "No mods discovered."
        
        summary = []
        summary.append(f"📋 Discovery Summary: {len(self.discovered_mods)} mods found")
        summary.append("")
        
        for i, mod_info in enumerate(self.discovered_mods, 1):
            summary.append(f"{i}. {mod_info.mod_name}")
            
            if mod_info.esp_file:
                summary.append(f"   🎯 Plugin: {mod_info.esp_name}.{mod_info.esp_type.lower()}")
            elif mod_info.available_plugins:
                summary.append(f"   🔍 Multiple plugins ({len(mod_info.available_plugins)}):")
                for j, (plugin_path, plugin_type) in enumerate(mod_info.available_plugins):
                    plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
                    summary.append(f"      {j+1}. {plugin_name}.{plugin_type.lower()}")
            
            if mod_info.available_folders:
                summary.append(f"   📁 Asset folders ({len(mod_info.available_folders)}):")
                for folder_path in mod_info.available_folders:
                    folder_name = os.path.basename(folder_path)
                    summary.append(f"      - {folder_name}")
            
            summary.append(f"   📊 Assets: {len(mod_info.asset_files)} files ({format_bytes(mod_info.asset_size)})")
            summary.append("")
        
        return "\n".join(summary)
    
    def check_bsarch_availability(self, force_refresh: bool = False) -> Tuple[bool, str]:
        """
        Check if BSArch is available using universal BSArch service.
        
        Args:
            force_refresh: Whether to force refresh and clear cache
        
        Returns:
            Tuple of (is_available: bool, message: str)
        """
        try:
            from .bsarch_service import check_bsarch_availability_universal
            
            # Use universal BSArch service (interactive for batch repacker)
            success, message = check_bsarch_availability_universal(
                game_type=self.game_type, 
                interactive=True,
                force_refresh=force_refresh
            )
            return success, message
            
        except Exception as e:
            return False, f"Error checking BSArch: {e}"
    
    @classmethod
    def load_config_from_file(cls, config_path: str) -> Dict:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log(f"⚠️  Configuration file not found: {config_path}", log_type='WARNING')
            return {}
        except json.JSONDecodeError as e:
            log(f"❌ Invalid JSON in configuration file: {e}", log_type='ERROR')
            return {}
        except Exception as e:
            log(f"❌ Error loading configuration: {e}", log_type='ERROR')
            return {}
    
    @classmethod
    def create_from_config_file(cls, config_path: str, game_type: str = "skyrim", threads: int = 8):
        """
        Create BatchModRepacker instance from a configuration file.
        
        Args:
            config_path: Path to JSON configuration file
            game_type: Target game type
            threads: Number of processing threads
            
        Returns:
            Configured BatchModRepacker instance
        """
        config = cls.load_config_from_file(config_path)
        return cls(game_type=game_type, threads=threads, config=config)
    
    @classmethod
    def create_with_game_preset(cls, game_type: str, threads: int = 8):
        """
        Create BatchModRepacker with automatic game-specific preset.
        Perfect for non-technical users - no configuration needed!
        
        Args:
            game_type: Game type ("skyrim", "fallout4", "fallout3", "oblivion", "bodyslide")
            threads: Number of processing threads
            
        Returns:
            Pre-configured BatchModRepacker instance
        """
        # Map game types to unified config system
        game_mapping = {
            'skyrim': 'skyrim',
            'skyrim_se': 'skyrim', 
            'skyrim_special_edition': 'skyrim',
            'fallout4': 'fallout4',
            'fallout_4': 'fallout4',
            'f4': 'fallout4',
            'fallout3': 'fallout3',
            'fallout_3': 'fallout3',
            'f3': 'fallout3',
            'oblivion': 'oblivion',
            'tes4': 'oblivion',
            'bodyslide': 'bodyslide',
            'body_slide': 'bodyslide',
            'caliente': 'bodyslide'
        }
        
        game_key = game_type.lower().replace(' ', '_')
        
        if game_key not in game_mapping:
            log(f"⚠️  No preset found for game '{game_type}', using default configuration", log_type='WARNING')
            return cls(game_type=game_type, threads=threads)
        
        # Use default configuration (no game-specific configs needed)
        log(f"✅ Using default configuration for {game_type}", debug_only=True, log_type='SUCCESS')
        return cls(game_type=game_type, threads=threads)
        
    def discover_mods(self, collection_path: str) -> List[ModInfo]:
        """
        Discover all mods in a collection folder.
        
        Args:
            collection_path: Path to folder containing mod subfolders
            
        Returns:
            List of ModInfo objects for discovered mods
        """
        log(f"🔍 Discovering mods in: {collection_path}", log_type='INFO')
        discovered = []
        
        if not os.path.exists(collection_path) or not os.path.isdir(collection_path):
            log(f"❌ Collection path does not exist or is not a directory: {collection_path}", log_type='ERROR')
            return discovered
        
        try:
            # Look for mod folders (first level subdirectories)
            for item in os.listdir(collection_path):
                item_path = os.path.join(collection_path, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # Look for ESP/ESL/ESM files in this folder
                mod_info = self._analyze_mod_folder(item_path)
                if mod_info:
                    discovered.append(mod_info)
                    log(f"✅ Found mod: {mod_info.mod_name} ({mod_info.esp_type})", log_type='SUCCESS')
                else:
                    log(f"⚠️  Skipped folder (no plugin found): {item}", log_type='WARNING')
        
        except Exception as e:
            log(f"❌ Error discovering mods: {e}", log_type='ERROR')
        
        self.discovered_mods = discovered
        log(f"🎯 Discovery complete: {len(discovered)} mods found", log_type='SUCCESS')
        return discovered
    
    def _analyze_mod_folder(self, mod_path: str) -> Optional[ModInfo]:
        """
        Analyze a single mod folder to extract information.
        
        Args:
            mod_path: Path to mod folder
            
        Returns:
            ModInfo object if valid mod found, None otherwise
        """
        try:
            # Find ESP/ESL/ESM files
            plugin_files = []
            asset_files = []
            asset_folders = set()
            total_asset_size = 0
            
            for root, dirs, files in safe_walk(mod_path, followlinks=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    # Check for plugin files
                    for ext in self.config['plugin_extensions']:
                        if file_lower.endswith(ext.lower()):
                            plugin_type = ext[1:].upper()  # Remove dot and uppercase
                            plugin_files.append((file_path, plugin_type))
                            break
                    else:
                        # Check for asset files (anything that's not a plugin)
                        if self._is_game_asset(file_lower):
                            asset_files.append(file_path)
                            try:
                                total_asset_size += os.path.getsize(file_path)
                            except OSError:
                                pass
                
                # Track ALL folders (both packable and unpackable)
                for dir_name in dirs:
                    dir_lower = dir_name.lower()
                    # Add all folders to available_folders (we'll filter later)
                    if dir_lower in ['meshes', 'textures', 'scripts', 'sounds', 'music', 'interface', 'materials', 'lodsettings', 'seq', 'facegen', 'shadersfx'] or is_unpackable_folder(dir_name, self.game_type):
                        asset_folders.add(os.path.join(root, dir_name))
            
            # Must have at least one plugin file
            if len(plugin_files) == 0:
                log(f"⚠️  No plugin file found in: {os.path.basename(mod_path)}", debug_only=True, log_type='WARNING')
                return None
            
            # Must have some assets to be worth repacking
            if len(asset_files) == 0:
                log(f"⚠️  No assets found in: {os.path.basename(mod_path)}", debug_only=True, log_type='WARNING')
                return None
            
            # Create ModInfo with all discovered information
            mod_info = ModInfo(mod_path, game_type=self.game_type)
            mod_info.available_plugins = plugin_files
            mod_info.available_folders = list(asset_folders)
            mod_info.asset_files = asset_files
            mod_info.asset_size = total_asset_size
            
            # If only one plugin, auto-select it
            if len(plugin_files) == 1:
                plugin_path, plugin_type = plugin_files[0]
                mod_info.esp_file = plugin_path
                mod_info.esp_name = os.path.splitext(os.path.basename(plugin_path))[0]
                mod_info.esp_type = plugin_type
                log(f"✅ Found mod: {mod_info.mod_name} ({plugin_type})", log_type='SUCCESS')
            else:
                log(f"🔍 Found mod with multiple plugins: {mod_info.mod_name} ({len(plugin_files)} plugins)", log_type='INFO')
            
            # Simple categorization - just note that we have assets
            if asset_files:
                mod_info.asset_categories.add('assets')  # Simple: we have assets to pack
            
            return mod_info
            
        except Exception as e:
            log(f"❌ Error analyzing mod folder {mod_path}: {e}", debug_only=True, log_type='ERROR')
            return None
    
    def _is_game_asset(self, filename: str) -> bool:
        """
        Check if a file should be packed as an asset.
        Simple rule: pack everything except plugin files and common junk.
        
        Args:
            filename: Lowercase filename to check
            
        Returns:
            True if file should be packed
        """
        # Skip plugin files - they're handled separately
        for ext in self.config['plugin_extensions']:
            if filename.endswith(ext.lower()):
                return False
        
        # Skip common junk files
        junk_files = {'.ds_store', 'thumbs.db', 'desktop.ini', '.gitignore', 'readme.txt'}
        if filename in junk_files:
            return False
        
        # Skip temporary files
        if filename.startswith('.') or filename.endswith('.tmp') or filename.endswith('.bak'):
            return False
        
        # Everything else is an asset to pack
        return True
    
    def process_mod_collection(self, 
                              collection_path: str, 
                              output_path: str,
                              progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Process an entire collection of mods.
        
        Args:
            collection_path: Path to folder containing mod subfolders
            output_path: Path where repacked mods should be saved
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with processing results
        """
        log(f"🚀 Starting batch mod repacking...", log_type='INFO')
        log(f"   Source: {collection_path}", log_type='INFO')
        log(f"   Output: {output_path}", log_type='INFO')
        
        # Use already discovered mods if available, otherwise discover them
        if self.discovered_mods:
            mods = self.discovered_mods
            log(f"📋 Using {len(mods)} pre-discovered mods with user selections", log_type='INFO')
        else:
            mods = self.discover_mods(collection_path)
            if not mods:
                return {
                    'success': False,
                    'message': 'No valid mods found in collection',
                    'processed': 0,
                    'failed': 0,
                    'total': 0
                }
        
        # Check output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Check available disk space
        total_size = sum(mod.asset_size for mod in mods)
        has_space, available, required = check_disk_space(output_path, total_size * 3)  # 3x for temp files
        if not has_space:
            return {
                'success': False,
                'message': f'Insufficient disk space: need {format_bytes(required)}, have {format_bytes(available)}',
                'processed': 0,
                'failed': 0,
                'total': len(mods)
            }
        
        # Process each mod
        self.processed_mods = []
        self.failed_mods = []
        
        for i, mod_info in enumerate(mods):
            if progress_callback:
                progress_callback(i, len(mods), f"Processing {mod_info.mod_name}")
            
            try:
                log(f"📦 Processing mod {i+1}/{len(mods)}: {mod_info.mod_name}", log_type='INFO')
                
                # Handle multiple plugins - only auto-select if user hasn't already chosen
                if not mod_info.esp_file and mod_info.available_plugins:
                    self.select_plugin_for_mod(mod_info, 0)  # Select first plugin
                    log(f"🔧 Auto-selected plugin: {mod_info.esp_name}", log_type='INFO')
                elif mod_info.esp_file:
                    log(f"🔧 Using user-selected plugin: {mod_info.esp_name}", log_type='INFO')
                
                # Handle folder selection - auto-select all folders for now
                if mod_info.available_folders:
                    self.select_folders_for_mod(mod_info, None)  # Select all folders
                    log(f"📁 Auto-selected {len(mod_info.available_folders)} asset folders", log_type='INFO')
                
                success, result_path = self._batch_repack_process_single_mod(mod_info, output_path)
                
                if success:
                    self.processed_mods.append((mod_info, result_path))
                    log(f"✅ Successfully processed: {mod_info.mod_name}", log_type='SUCCESS')
                else:
                    self.failed_mods.append((mod_info, result_path))  # result_path contains error message
                    log(f"❌ Failed to process: {mod_info.mod_name} - {result_path}", log_type='ERROR')
                    
            except Exception as e:
                self.failed_mods.append((mod_info, str(e)))
                log(f"❌ Exception processing {mod_info.mod_name}: {e}", log_type='ERROR')
        
        # Final progress update
        if progress_callback:
            progress_callback(len(mods), len(mods), "Batch processing complete")
        
        # Summary
        processed_count = len(self.processed_mods)
        failed_count = len(self.failed_mods)
        
        log(f"🎉 Batch processing complete!", log_type='SUCCESS')
        log(f"   ✅ Successfully processed: {processed_count} mods", log_type='SUCCESS')
        log(f"   ❌ Failed: {failed_count} mods", log_type='ERROR' if failed_count > 0 else 'INFO')
        
        return {
            'success': True,
            'message': f'Processed {processed_count}/{len(mods)} mods successfully',
            'processed': processed_count,
            'failed': failed_count,
            'total': len(mods),
            'processed_mods': self.processed_mods,
            'failed_mods': self.failed_mods
        }
    
    def _batch_repack_process_single_mod(self, mod_info: ModInfo, output_path: str) -> Tuple[bool, str]:
        """
        Process a single mod during batch repacking.
        
        Args:
            mod_info: ModInfo object with mod details
            output_path: Base output directory
            
        Returns:
            Tuple of (success, result_path_or_error_message)
        """
        try:
            # Create temporary directories for processing
            with tempfile.TemporaryDirectory(prefix=f"batch_repack_{mod_info.esp_name}_") as temp_dir:
                # Step 1: Classify files (all assets are "new" since we're repacking existing mods)
                pack_dir = os.path.join(temp_dir, "pack")
                os.makedirs(pack_dir, exist_ok=True)
                
                # Apply folder selection if available
                asset_files_to_process = mod_info.asset_files
                if hasattr(mod_info, 'selected_folders') and mod_info.selected_folders:
                    # Filter asset files to only include those from selected folders
                    asset_files_to_process = []
                    for asset_file in mod_info.asset_files:
                        asset_dir = os.path.dirname(asset_file)
                        if any(asset_dir.startswith(folder) for folder in mod_info.selected_folders):
                            asset_files_to_process.append(asset_file)
                    log(f"📁 Using {len(asset_files_to_process)} files from selected folders", debug_only=True, log_type='INFO')
                
                # Copy selected asset files to pack directory
                log(f"📋 Classifying {len(asset_files_to_process)} asset files...", debug_only=True, log_type='INFO')
                
                for asset_file in asset_files_to_process:
                    # Calculate relative path from mod root
                    rel_path = os.path.relpath(asset_file, mod_info.mod_path)
                    dest_path = os.path.join(pack_dir, rel_path)
                    
                    # Create destination directory
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(asset_file, dest_path)
                
                # Step 2: Create BSA/BA2 archive from assets only
                from .packaging.archive_creator import ArchiveCreator
                archive_creator = ArchiveCreator(game_type=self.game_type)
                
                # Recursively find all asset files
                asset_files = []
                for root, dirs, files in os.walk(pack_dir):
                    for file in files:
                        asset_files.append(os.path.join(root, file))
                
                if not asset_files:
                    return False, "No asset files found to pack"
                
                # Create BSA/BA2 archive(s) with plugin name (may create chunks)
                bsa_path = os.path.join(temp_dir, f"{mod_info.esp_name}")
                log(f"📦 Creating {self.game_type.upper()} archive(s): {mod_info.esp_name}", debug_only=True, log_type='INFO')
                
                archive_success, archive_message = archive_creator.create_archive(
                    asset_files, bsa_path, mod_info.esp_name
                )
                
                if not archive_success:
                    return False, f"Archive creation failed: {archive_message}"
                
                # Find all created archive files (may be multiple chunks)
                archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
                
                created_archives = []
                
                # Look for BSA/BA2 files only (no ZIP fallback - ZIP is not a valid game archive format)
                for file in os.listdir(temp_dir):
                    if file.startswith(mod_info.esp_name) and file.endswith(archive_ext):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.exists(file_path):
                            created_archives.append(file_path)
                
                if not created_archives:
                    return False, f"No archive files found for {mod_info.esp_name}"
                
                # Log created archives
                if len(created_archives) == 1:
                    log(f"✅ Created single archive: {os.path.basename(created_archives[0])} ({os.path.getsize(created_archives[0])} bytes)", debug_only=True, log_type='INFO')
                else:
                    log(f"✅ Created {len(created_archives)} chunked archives:", debug_only=True, log_type='INFO')
                    total_size = 0
                    for archive_path in created_archives:
                        size = os.path.getsize(archive_path)
                        total_size += size
                        log(f"  • {os.path.basename(archive_path)} ({size} bytes)", debug_only=True, log_type='INFO')
                    log(f"📊 Total chunked size: {total_size} bytes", debug_only=True, log_type='INFO')
                
                # Step 3: Copy original plugin file (keep original ESP/ESL/ESM)
                plugin_dest = os.path.join(temp_dir, f"{mod_info.esp_name}.{mod_info.esp_type.lower()}")
                shutil.copy2(mod_info.esp_file, plugin_dest)
                log(f"📄 Copied original {mod_info.esp_type}: {os.path.basename(mod_info.esp_file)}", debug_only=True, log_type='INFO')
                
                # Step 3.5: Copy unpackable folders (blacklisted folders that should stay loose)
                unpackable_folders_copied = []
                if hasattr(mod_info, 'available_folders') and mod_info.available_folders:
                    from .constants import get_unpackable_folders_from_list
                    folder_names = [os.path.basename(folder) for folder in mod_info.available_folders]
                    unpackable_folder_names = get_unpackable_folders_from_list(folder_names, mod_info.game_type)
                    
                    for folder_path in mod_info.available_folders:
                        folder_name = os.path.basename(folder_path)
                        if folder_name in unpackable_folder_names:
                            # Copy unpackable folder to temp directory
                            dest_folder = os.path.join(temp_dir, folder_name)
                            shutil.copytree(folder_path, dest_folder, dirs_exist_ok=True)
                            unpackable_folders_copied.append(folder_name)
                            log(f"📦 Copied unpackable folder: {folder_name}", debug_only=True, log_type='INFO')
                
                if unpackable_folders_copied:
                    log(f"📦 Unpackable folders included: {', '.join(unpackable_folders_copied)}", debug_only=True, log_type='INFO')
                
                # Step 4: Create final 7z package with BSA + original plugin + unpackable folders
                # Create final package name using configurable naming pattern
                naming = self.config['package_naming']
                if naming['use_esp_name']:
                    base_name = mod_info.esp_name
                else:
                    base_name = mod_info.mod_name
                
                final_package_name = f"{base_name}{naming['separator']}{naming['version']}{naming['suffix']}.7z"
                final_package_path = os.path.join(output_path, final_package_name)
                
                # Use our new compression method to pack BSA + plugin
                from .packaging.compression_service import Compressor
                compressor = Compressor(compression_level=7)
                
                # Create a clean temporary folder with only the final files
                final_temp_dir = os.path.join(temp_dir, "final")
                os.makedirs(final_temp_dir, exist_ok=True)
                
                # Copy all BSA/BA2 chunks and plugin files to final temp directory
                final_plugin_path = os.path.join(final_temp_dir, os.path.basename(plugin_dest))
                shutil.copy2(plugin_dest, final_plugin_path)
                
                # Copy all archive chunks
                for archive_path in created_archives:
                    final_archive_path = os.path.join(final_temp_dir, os.path.basename(archive_path))
                    shutil.copy2(archive_path, final_archive_path)
                    log(f"📦 Copied archive chunk: {os.path.basename(archive_path)}", log_type='INFO')
                
                # Copy blacklisted folders to final temp directory
                for folder_name in unpackable_folders_copied:
                    source_folder = os.path.join(temp_dir, folder_name)
                    dest_folder = os.path.join(final_temp_dir, folder_name)
                    if os.path.exists(source_folder):
                        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
                        log(f"📦 Copied blacklisted folder to final package: {folder_name}", log_type='INFO')
                    else:
                        log(f"⚠️ Blacklisted folder not found in temp dir: {source_folder}", log_type='WARNING')
                
                # Debug: Show what's in the final temp directory
                final_contents = []
                for root, dirs, files in os.walk(final_temp_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), final_temp_dir)
                        final_contents.append(rel_path)
                    for dir_name in dirs:
                        rel_path = os.path.relpath(os.path.join(root, dir_name), final_temp_dir)
                        final_contents.append(rel_path + '/')
                
                log(f"📦 Final package contents: {final_contents}", log_type='INFO')
                
                # Compress only the final files with proper folder structure
                compress_success, compress_message = compressor.compress_directory_with_folder_name(
                    source_dir=final_temp_dir,
                    archive_path=final_package_path,
                    folder_name=base_name
                )
                
                if not compress_success:
                    return False, f"Final compression failed: {compress_message}"
                
                return True, final_package_path
                
        except Exception as e:
            return False, str(e)
    
    def get_summary_report(self) -> str:
        """
        Generate a summary report of the batch processing.
        
        Returns:
            Formatted summary report string
        """
        if not hasattr(self, 'processed_mods') or not hasattr(self, 'failed_mods'):
            return "No batch processing has been performed yet."
        
        report = []
        report.append("🎯 BATCH MOD REPACKING SUMMARY")
        report.append("=" * 50)
        report.append(f"Total mods discovered: {len(self.discovered_mods)}")
        report.append(f"Successfully processed: {len(self.processed_mods)}")
        report.append(f"Failed: {len(self.failed_mods)}")
        report.append("")
        
        if self.processed_mods:
            report.append("✅ SUCCESSFULLY PROCESSED:")
            for mod_info, result_path in self.processed_mods:
                size_str = format_bytes(mod_info.asset_size)
                report.append(f"  • {mod_info.mod_name} ({mod_info.esp_type}, {size_str})")
                report.append(f"    → {os.path.basename(result_path)}")
            report.append("")
        
        if self.failed_mods:
            report.append("❌ FAILED TO PROCESS:")
            for mod_info, error_msg in self.failed_mods:
                report.append(f"  • {mod_info.mod_name} ({mod_info.esp_type})")
                report.append(f"    Error: {error_msg}")
            report.append("")
        
        return "\n".join(report)
