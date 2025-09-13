"""
Package Builder - Complete mod packaging automation

Orchestrates the complete packaging pipeline from classification to final distribution package.
Creates BSA/BA2 archives, ESP files, compressed loose files, and final 7z packages.
"""

import os
import json
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from ..dynamic_progress import log
from .archive_creator import ArchiveCreator
from .esp_manager import ESPManager
from .compression_service import Compressor


class PackageBuilder:
    """Main orchestrator for complete mod package creation."""

    def __init__(self,
                 game_type: str = "skyrim",
                 compression_level: int = 3,
                 template_dir: Optional[str] = None):
        """
        Initialize package builder.

        Args:
            game_type: Target game ("skyrim" or "fallout4")
            compression_level: 7z compression level (0-9)
            template_dir: Directory containing ESP templates
        """
        self.game_type = game_type.lower()
        self.compression_level = compression_level

        # Initialize components
        self.archive_creator = ArchiveCreator(game_type)
        self.esp_manager = ESPManager(template_dir)
        self.compressor = Compressor(compression_level)

        # Package metadata
        self.package_info = {}
        self.build_log = []

    def build_complete_package(self,
                              classification_results: Dict[str, List[str]],
                              mod_name: str,
                              output_dir: str,
                              options: Optional[Dict[str, Any]] = None,
                              esp_name: Optional[str] = None,
                              archive_name: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Build complete mod package from classification results.

        Args:
            classification_results: Results from SafeResourcePacker classification
            mod_name: Name of the mod
            output_dir: Directory to create package in
            options: Additional options for package creation
            esp_name: Name for ESP file (defaults to mod_name)
            archive_name: Name for archive file (defaults to mod_name)

        Returns:
            Tuple of (success: bool, package_path: str, package_info: dict)
        """
        options = options or {}
        
        # Set defaults for ESP and archive names
        esp_name = esp_name or mod_name
        archive_name = archive_name or mod_name
        
        self._log_build_step(f"Starting package build for '{mod_name}'")

        try:
            # Validate inputs
            if not self._validate_inputs(classification_results, mod_name, output_dir):
                return False, "", {}

            # Build components directly (no duplicate work!)
            success, package_info = self._build_separate_components(
                classification_results, mod_name, output_dir, options, esp_name, archive_name
            )
            
            if success:
                # Generate metadata in the output directory  
                self._generate_clean_metadata(output_dir, mod_name, package_info, options)
                self._log_build_step("Components created successfully")
                return True, output_dir, package_info
            else:
                return False, "", {}

        except Exception as e:
            error_msg = f"Package build failed: {e}"
            self._log_build_step(error_msg, is_error=True)
            log(error_msg, log_type='ERROR')
            return False, "", {}

    def _validate_inputs(self,
                        classification_results: Dict[str, List[str]],
                        mod_name: str,
                        output_dir: str) -> bool:
        """Validate input parameters."""

        if not classification_results:
            log("No classification results provided", log_type='ERROR')
            return False

        if not mod_name or not mod_name.strip():
            log("Mod name is required", log_type='ERROR')
            return False

        # Sanitize mod name
        invalid_chars = '<>:"/\\|?*'
        if any(char in mod_name for char in invalid_chars):
            log(f"Mod name contains invalid characters: {invalid_chars}", log_type='ERROR')
            return False

        # Check if we have files to package
        total_files = sum(len(files) for files in classification_results.values())
        if total_files == 0:
            log("No files found in classification results", log_type='ERROR')
            return False

        return True


    def _build_separate_components(self,
                                 classification_results: Dict[str, List[str]],
                                 mod_name: str,
                                 output_dir: str,
                                 options: Dict[str, Any],
                                 esp_name: str = None,
                                 archive_name: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Build components as separate outputs: BSA+ESP, Loose 7z, and Metadata."""
        
        # Set defaults
        esp_name = esp_name or mod_name
        archive_name = archive_name or mod_name
        
        package_info = {
            "mod_name": mod_name,
            "game_type": self.game_type,
            "created": datetime.now().isoformat(),
            "components": {}
        }

        # 1. Create BSA/BA2 + ESP package (packed side)
        if 'pack' in classification_results and classification_results['pack']:
            packed_success = self._create_packed_archive(
                classification_results['pack'], mod_name, output_dir, package_info, esp_name, archive_name
            )
            if not packed_success:
                return False, {}

        # 2. Create loose files 7z (loose side)  
        if 'loose' in classification_results and classification_results['loose']:
            loose_success = self._create_loose_archive(
                classification_results['loose'], mod_name, output_dir, package_info, options
            )
            if not loose_success:
                return False, {}

        # 3. Handle blacklisted files - include them in loose archive or create separate archive if no loose files
        if 'blacklisted' in classification_results and classification_results['blacklisted']:
            if 'loose' in classification_results and classification_results['loose']:
                # Blacklisted files already included in loose archive above
                log(f"🚫 {len(classification_results['blacklisted'])} blacklisted files included in loose archive", log_type='INFO')
            else:
                # No loose files - create separate archive for blacklisted files
                log(f"🚫 {len(classification_results['blacklisted'])} blacklisted files - creating separate archive", log_type='INFO')
                blacklisted_success = self._create_blacklisted_archive(
                    mod_name, output_dir, package_info, options
                )
                if not blacklisted_success:
                    return False, {}

        # 4. Final package creation removed - users get separate 7z archives
        has_pack = package_info.get("components", {}).get("pack")
        has_loose = package_info.get("components", {}).get("loose")
        has_blacklisted = package_info.get("components", {}).get("blacklisted")
        
        log(f"✅ Package creation complete: has_pack={bool(has_pack)}, has_loose={bool(has_loose)}, has_blacklisted={bool(has_blacklisted)}", log_type='INFO')
        if has_pack:
            log(f"📦 Packed archive: {os.path.basename(has_pack['path'])}", log_type='SUCCESS')
        if has_loose:
            log(f"📁 Loose archive: {os.path.basename(has_loose['path'])}", log_type='SUCCESS')
        if has_blacklisted:
            log(f"📁 Loose files archive: {os.path.basename(has_blacklisted['path'])}", log_type='SUCCESS')

        # Clean up temp blacklisted directory after successful packaging
        temp_blacklisted_dir = options.get('temp_blacklisted_dir')
        if temp_blacklisted_dir and os.path.exists(temp_blacklisted_dir):
            try:
                shutil.rmtree(temp_blacklisted_dir, ignore_errors=True)
                log(f"🧹 Cleaned up temp blacklisted directory: {temp_blacklisted_dir}", log_type='INFO')
            except Exception as e:
                log(f"⚠️ Failed to clean up temp blacklisted directory: {e}", log_type='WARNING')

        return True, package_info

    def _create_blacklisted_archive(self, mod_name: str,
                                   output_dir: str, package_info: Dict[str, Any], options: Dict[str, Any] = None) -> bool:
        """Create 7z archive for blacklisted files when no loose files exist."""
        self._log_build_step("Creating blacklisted files 7z archive")
        
        blacklisted_7z_path = os.path.join(output_dir, f"{mod_name}_Loose_Files.7z")
        
        # Create temporary directory for blacklisted files
        import tempfile
        with tempfile.TemporaryDirectory(prefix=f"blacklisted_archive_{mod_name}_") as temp_dir:
            blacklisted_items_count = 0
            
            # Copy blacklisted files from temp directory
            temp_blacklisted_dir = options.get('temp_blacklisted_dir')
            if temp_blacklisted_dir and os.path.exists(temp_blacklisted_dir):
                log(f"🚫 Copying blacklisted files from temp directory: {temp_blacklisted_dir}", log_type='INFO')
                for root, dirs, files in os.walk(temp_blacklisted_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_blacklisted_dir)
                        dest_path = os.path.join(temp_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(src_path, dest_path)
                        blacklisted_items_count += 1
                        log(f"📄 Added blacklisted file: {rel_path}", log_type='SPAM')
                
                if blacklisted_items_count == 0:
                    log(f"⚠️ No blacklisted items found in temp directory: {temp_blacklisted_dir}", log_type='WARNING')
                    return False
            else:
                log(f"❌ Temp blacklisted directory not found: {temp_blacklisted_dir}", log_type='ERROR')
                return False
            
            # Compress the blacklisted directory
            compression_success, compression_message = self.compressor.compress_directory_with_folder_name(
                temp_dir, blacklisted_7z_path, f"{mod_name}_Loose_Files"
            )
        
        if compression_success:
            package_info["components"]["blacklisted"] = {
                "path": blacklisted_7z_path,
                "file_count": blacklisted_items_count,
                "contains": "Loose files and folders (SKSE, MCM, etc.)"
            }
            self._log_build_step(f"Loose files archive created: {os.path.basename(blacklisted_7z_path)}")
            return True
        else:
            log(f"Blacklisted archive compression failed: {compression_message}", log_type='ERROR')
            return False

    def _copy_loose_files_from_extracted(self, loose_extract_dir: str, temp_dir: str, mod_name: str):
        """Copy loose files from extracted loose archive."""
        log(f"🔍 Looking for loose folder in: {loose_extract_dir}", log_type='DEBUG')
        
        # Look for the mod's loose folder in the extracted directory
        mod_loose_dir = os.path.join(loose_extract_dir, f"{mod_name}_Loose")
        if not os.path.exists(mod_loose_dir):
            log(f"⚠️ Expected loose folder not found: {mod_loose_dir}", log_type='WARNING')
            # Try alternative paths
            for item in os.listdir(loose_extract_dir):
                item_path = os.path.join(loose_extract_dir, item)
                if os.path.isdir(item_path) and mod_name.lower() in item.lower():
                    mod_loose_dir = item_path
                    log(f"🔍 Found alternative loose folder: {mod_loose_dir}", log_type='DEBUG')
                    break
        
        if os.path.exists(mod_loose_dir):
            log(f"📁 Processing loose folder: {mod_loose_dir}", log_type='DEBUG')
            # List all items in the loose folder
            loose_items = os.listdir(mod_loose_dir)
            log(f"📋 Loose folder contents: {loose_items}", log_type='DEBUG')
            
            # Copy all loose files and folders
            loose_copied = []
            for item in loose_items:
                item_path = os.path.join(mod_loose_dir, item)
                if os.path.isdir(item_path):
                    dest_path = os.path.join(temp_dir, item)
                    shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
                    loose_copied.append(item)
                    log(f"📁 Copied loose folder: {item}", log_type='INFO')
                elif os.path.isfile(item_path):
                    dest_path = os.path.join(temp_dir, item)
                    shutil.copy2(item_path, dest_path)
                    loose_copied.append(item)
                    log(f"📄 Copied loose file: {item}", log_type='INFO')
            
            if loose_copied:
                log(f"✅ Copied {len(loose_copied)} loose items: {loose_copied}", log_type='INFO')
            else:
                log(f"⚠️ No loose items found in loose directory", log_type='WARNING')
        else:
            log(f"❌ Loose folder not found: {mod_loose_dir}", log_type='ERROR')

    def _copy_blacklisted_folders_from_directory(self, blacklisted_dir: str, temp_dir: str):
        """Copy blacklisted folders from blacklisted directory."""
        log(f"🔍 Looking for blacklisted folders in: {blacklisted_dir}", log_type='DEBUG')
        
        if not os.path.exists(blacklisted_dir):
            log(f"❌ Blacklisted directory not found: {blacklisted_dir}", log_type='ERROR')
            return
        
        # Copy all contents from blacklisted directory to temp directory
        blacklisted_copied = []
        for item in os.listdir(blacklisted_dir):
            item_path = os.path.join(blacklisted_dir, item)
            if os.path.isdir(item_path):
                dest_path = os.path.join(temp_dir, item)
                shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
                blacklisted_copied.append(item)
                log(f"📦 Copied blacklisted folder: {item}", log_type='INFO')
            elif os.path.isfile(item_path):
                dest_path = os.path.join(temp_dir, item)
                shutil.copy2(item_path, dest_path)
                blacklisted_copied.append(item)
                log(f"📄 Copied blacklisted file: {item}", log_type='INFO')
        
        if blacklisted_copied:
            log(f"✅ Copied {len(blacklisted_copied)} blacklisted items: {blacklisted_copied}", log_type='INFO')
        else:
            log(f"⚠️ No blacklisted items found in blacklisted directory", log_type='WARNING')

    def _create_packed_archive(self, pack_files: List[str], mod_name: str, 
                              output_dir: str, package_info: Dict[str, Any],
                              esp_name: str = None, archive_name: str = None) -> bool:
        """Create game-specific BSA/BA2 + ESP archives following proper naming conventions."""
        # Set defaults
        esp_name = esp_name or mod_name
        archive_name = archive_name or mod_name
        
        # Use clean mod name for ESP (no _pack suffix needed)
        # esp_name is already set to mod_name or provided name
        
        self._log_build_step("Creating game-specific BSA/BA2 + ESP package")
        
        # Create temporary directory for staging files
        temp_dir = None
        try:
            temp_dir = self._create_temp_staging_directory(pack_files)
            if not temp_dir:
                return False
            
            # Use game-specific archive creation
            bsa_creation_success, bsa_creation_message, created_archives = self.archive_creator.create_game_specific_archives(
                pack_files, archive_name, output_dir, temp_dir
            )
            
            if not bsa_creation_success:
                log(f"Game-specific BSA/BA2 creation failed: {bsa_creation_message}", log_type='ERROR')
                return False
            
            if not created_archives:
                log(f"No archive files found for {archive_name}", log_type='ERROR')
                return False
            
            # Log created archives
            log(f"🎉 Created {len(created_archives)} archive(s) for {self.game_type}:", log_type='INFO')
            for archive in created_archives:
                archive_size = os.path.getsize(archive) / (1024 * 1024)  # MB
                log(f"  • {os.path.basename(archive)} ({archive_size:.1f} MB)", log_type='INFO')
            
            # 2. Create ESP file(s) for the archives
            esp_creation_success, esp_file_path = self.esp_manager.create_esp(
                esp_name, output_dir, self.game_type, created_archives
            )
            
            if not esp_creation_success:
                log(f"ESP creation failed: {esp_file_path}", log_type='ERROR')
                return False
            
            # Update package info
            package_info['archives'] = created_archives
            package_info['esp_file'] = esp_file_path
            package_info['archive_count'] = len(created_archives)
            
            # Handle multiple ESP files for chunked archives
            if isinstance(esp_file_path, list):
                package_info['esp_files'] = esp_file_path
                package_info['esp_count'] = len(esp_file_path)
            
            # Log ESP creation
            if isinstance(esp_file_path, list):
                log(f"📄 Created {len(esp_file_path)} ESP file(s) for chunked archives", log_type='SUCCESS')
            else:
                log(f"📄 ESP created: {os.path.basename(esp_file_path)}", log_type='SUCCESS')
            
            # 3. Create final 7z package containing all BSA/BA2 files and ESP plugins
            final_7z_success = self._create_final_7z_package(
                created_archives, esp_file_path, mod_name, output_dir
            )
            
            if not final_7z_success:
                log(f"Final 7z package creation failed", log_type='ERROR')
                return False
            
            # 4. Clean up individual BSA/ESP files after successful 7z packaging
            self._cleanup_packaged_files(created_archives, esp_file_path)
            
            return True
            
        except Exception as e:
            log(f"Error in packed archive creation: {e}", log_type='ERROR')
            return False
        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    log(f"🧹 Cleaned up temp staging directory", log_type='DEBUG')
                except Exception as cleanup_error:
                    log(f"Warning: Failed to cleanup temp directory: {cleanup_error}", log_type='WARNING')

    def _cleanup_packaged_files(self, created_archives: List[str], esp_file_path) -> None:
        """Clean up individual BSA/ESP files after they're packaged into final 7z."""
        try:
            files_cleaned = 0
            
            # Clean up BSA/BA2 archives
            for archive in created_archives:
                if os.path.exists(archive):
                    os.remove(archive)
                    files_cleaned += 1
                    log(f"🧹 Cleaned up archive: {os.path.basename(archive)}", log_type='DEBUG')
            
            # Clean up ESP files
            if isinstance(esp_file_path, list):
                # Multiple ESP files (chunked)
                for esp_file in esp_file_path:
                    if os.path.exists(esp_file):
                        os.remove(esp_file)
                        files_cleaned += 1
                        log(f"🧹 Cleaned up ESP: {os.path.basename(esp_file)}", log_type='DEBUG')
            else:
                # Single ESP file
                if os.path.exists(esp_file_path):
                    os.remove(esp_file_path)
                    files_cleaned += 1
                    log(f"🧹 Cleaned up ESP: {os.path.basename(esp_file_path)}", log_type='DEBUG')
            
            if files_cleaned > 0:
                log(f"🧹 Cleaned up {files_cleaned} individual files after 7z packaging", log_type='INFO')
            
        except Exception as e:
            log(f"Warning: Failed to cleanup some packaged files: {e}", log_type='WARNING')

    def _create_temp_staging_directory(self, pack_files: List[str]) -> Optional[str]:
        """Create temporary directory and stage files for archiving."""
        try:
            temp_dir = tempfile.mkdtemp(prefix="safe_resource_packer_")
            log(f"📁 Created temp staging directory: {temp_dir}", log_type='DEBUG')
            
            # Copy files to temp directory maintaining Data structure
            staged_count = 0
            for file_path in pack_files:
                if os.path.exists(file_path):
                    # Extract Data-relative path
                    data_rel_path = self._extract_data_relative_path(file_path)
                    if data_rel_path:
                        staged_path = os.path.join(temp_dir, data_rel_path)
                        staged_dir = os.path.dirname(staged_path)
                        
                        # Create directory structure
                        os.makedirs(staged_dir, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(file_path, staged_path)
                        staged_count += 1
            
            log(f"📋 Staged {staged_count} files for archiving", log_type='DEBUG')
            return temp_dir
            
        except Exception as e:
            log(f"Failed to create temp staging directory: {e}", log_type='ERROR')
            return None

    def _extract_data_relative_path(self, file_path: str) -> Optional[str]:
        """Extract Data-relative path from full file path."""
        try:
            # Find 'Data' in the path (case insensitive)
            path_parts = file_path.replace('\\', '/').split('/')
            data_index = -1
            
            for i, part in enumerate(path_parts):
                if part.lower() == 'data':
                    data_index = i
                    break
            
            if data_index >= 0 and data_index < len(path_parts) - 1:
                # Return path relative to Data folder
                return '/'.join(path_parts[data_index + 1:])
            
            return None
            
        except Exception:
            return None

    def _create_final_7z_package(self, 
                               created_archives: List[str], 
                               esp_file_path: str, 
                               mod_name: str, 
                               output_dir: str) -> bool:
        """Create final 7z package containing all BSA/BA2 files and ESP plugins."""
        try:
            # Collect all files to include in the final package
            files_to_package = []
            
            # Add all BSA/BA2 archives
            for archive in created_archives:
                if os.path.exists(archive):
                    files_to_package.append(archive)
            
            # Add ESP file(s)
            if isinstance(esp_file_path, list):
                # Multiple ESP files (chunked)
                for esp_file in esp_file_path:
                    if os.path.exists(esp_file):
                        files_to_package.append(esp_file)
            else:
                # Single ESP file
                if os.path.exists(esp_file_path):
                    files_to_package.append(esp_file_path)
            
            if not files_to_package:
                log(f"No files found to package in final 7z", log_type='ERROR')
                return False
            
            # Create final 7z package name (with _pack suffix to distinguish from loose files)
            final_package_name = f"{mod_name}_pack.7z"
            final_package_path = os.path.join(output_dir, final_package_name)
            
            log(f"📦 Creating final 7z package: {final_package_name}", log_type='INFO')
            log(f"📦 Including {len(files_to_package)} files:", log_type='INFO')
            for file_path in files_to_package:
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                log(f"  • {os.path.basename(file_path)} ({file_size:.1f} MB)", log_type='INFO')
            
            # Create temporary directory for staging files
            with tempfile.TemporaryDirectory(prefix="final_7z_") as temp_staging:
                # Copy all files to temp staging directory
                for file_path in files_to_package:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(temp_staging, filename)
                    shutil.copy2(file_path, dest_path)
                
                # Compress the staging directory
                success, message = self.compressor.compress_bulk_directory(temp_staging, final_package_path)
                
                if success:
                    final_size = os.path.getsize(final_package_path) / (1024 * 1024)  # MB
                    log(f"✅ Final 7z package created: {final_package_name} ({final_size:.1f} MB)", log_type='SUCCESS')
                    return True
                else:
                    log(f"❌ Final 7z package creation failed: {message}", log_type='ERROR')
                    return False
                    
        except Exception as e:
            log(f"Error creating final 7z package: {e}", log_type='ERROR')
            return False

    def _create_loose_archive(self, loose_files: List[str], mod_name: str,
                             output_dir: str, package_info: Dict[str, Any], options: Dict[str, Any] = None) -> bool:
        """Create 7z archive for loose files (including blacklisted files)."""
        self._log_build_step("Creating loose files 7z archive")
        
        loose_7z_path = os.path.join(output_dir, f"{mod_name}_loose.7z")
        
        # Create temporary directory to combine loose files and blacklisted files
        import tempfile
        with tempfile.TemporaryDirectory(prefix=f"loose_archive_{mod_name}_") as temp_dir:
            loose_items_count = 0
            blacklisted_items_count = 0
            
            # 1. Copy loose files
            if loose_files:
                loose_source_folder = options.get('output_loose')
                if not loose_source_folder:
                    # Fallback: use common path of loose files
                    loose_source_folder = os.path.commonpath(loose_files)
                    log(f"⚠️ No output_loose in options, using common path: {loose_source_folder}", log_type='WARNING')
                else:
                    log(f"Using user-defined loose folder: {loose_source_folder}", log_type='DEBUG')
                
                if os.path.exists(loose_source_folder):
                    # Copy all contents from loose folder to temp directory
                    for item in os.listdir(loose_source_folder):
                        item_path = os.path.join(loose_source_folder, item)
                        dest_path = os.path.join(temp_dir, item)
                        if os.path.isdir(item_path):
                            shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
                            loose_items_count += 1
                        elif os.path.isfile(item_path):
                            shutil.copy2(item_path, dest_path)
                            loose_items_count += 1
                    log(f"📁 Copied {loose_items_count} loose items to temp directory", log_type='DEBUG')
            
            # 2. Copy blacklisted files (if any) - from temp directory
            temp_blacklisted_dir = options.get('temp_blacklisted_dir')
            if temp_blacklisted_dir and os.path.exists(temp_blacklisted_dir):
                log(f"🚫 Adding blacklisted files from temp directory: {temp_blacklisted_dir}", log_type='DEBUG')
                for root, dirs, files in os.walk(temp_blacklisted_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_blacklisted_dir)
                        dest_path = os.path.join(temp_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(src_path, dest_path)
                        blacklisted_items_count += 1
                        log(f"📄 Added blacklisted file: {rel_path}", log_type='SPAM')
                
                if blacklisted_items_count > 0:
                    log(f"🚫 Added {blacklisted_items_count} blacklisted items to loose archive", log_type='INFO')
            
            # 3. Compress the combined temp directory
            if loose_items_count > 0 or blacklisted_items_count > 0:
                loose_compression_success, loose_compression_message = self.compressor.compress_directory_with_folder_name(
                    temp_dir,
                    loose_7z_path,
                    f"{mod_name}_Loose"
                )
            else:
                loose_compression_success, loose_compression_message = False, "No loose or blacklisted files found"
        
        if loose_compression_success:
            total_items = loose_items_count + blacklisted_items_count
            package_info["components"]["loose"] = {
                "path": loose_7z_path,
                "file_count": total_items,
                "contains": f"Override files ({loose_items_count} loose + {blacklisted_items_count} blacklisted)"
            }
            self._log_build_step(f"Loose archive created: {os.path.basename(loose_7z_path)} ({total_items} items)")
            return True
        else:
            log(f"Loose archive creation failed: {loose_compression_message}", log_type='ERROR')
            return False



    def _generate_clean_metadata(self,
                                output_dir: str,
                                mod_name: str,
                                package_info: Dict[str, Any],
                                options: Dict[str, Any]):
        """Generate clean metadata folder with proper formatting (no special characters)."""
        
        metadata_dir = os.path.join(output_dir, "Metadata")
        os.makedirs(metadata_dir, exist_ok=True)

        # 1. Clean package info JSON
        info_path = os.path.join(metadata_dir, "package_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, default=str, ensure_ascii=False)

        # 2. Clean installation instructions
        instructions_path = os.path.join(metadata_dir, "INSTALLATION.txt")
        self._generate_clean_instructions(instructions_path, mod_name, package_info)

        # 3. Clean build log
        log_path = os.path.join(metadata_dir, "build_log.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Build Log for {mod_name}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
            for entry in self.build_log:
                # Clean the entry of any special characters
                clean_entry = entry.replace('\\n', '\n').replace('\\t', '\t')
                f.write(f"{clean_entry}\n")

        # 4. Clean file summary
        summary_path = os.path.join(metadata_dir, "SUMMARY.txt")
        self._generate_clean_summary(summary_path, mod_name, package_info)

        self._log_build_step("Generated clean metadata")

    def _generate_clean_instructions(self,
                                   instructions_path: str,
                                   mod_name: str,
                                   package_info: Dict[str, Any]):
        """Generate clean installation instructions without special characters."""
        
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(f"INSTALLATION INSTRUCTIONS - {mod_name}\n")
            f.write("=" * 50 + "\n\n")

            f.write("This package was created by Safe Resource Packer\n")
            f.write("It contains optimized archives and loose override files.\n\n")

            # Instructions for packed archive
            if "packed" in package_info.get("components", {}):
                f.write("1. PACKED FILES (BSA/BA2 + ESP) - READY TO INSTALL:\n")
                f.write("   - Extract the *_Packed.7z file\n")
                f.write("   - Install the BSA/BA2 and ESP files to your game Data folder\n")
                f.write("   - Enable the ESP in your mod manager\n")
                f.write("   - BSA/BA2 archives were automatically created for optimal performance\n\n")

            # Instructions for loose files
            if "loose" in package_info.get("components", {}):
                f.write("2. LOOSE FILES (Override Files):\n")
                f.write("   - Extract the *_loose.7z file\n")
                f.write("   - Copy the loose files to your game Data folder\n")
                f.write("   - These files will override the BSA/BA2 content when needed\n\n")

            f.write("3. LOAD ORDER:\n")
            f.write("   - Place the ESP where appropriate in your load order\n")
            f.write("   - Loose files automatically override archives\n")
            f.write("   - BSA/BA2 archives provide better game performance than loose files\n\n")

            f.write("4. TROUBLESHOOTING:\n")
            f.write("   - If textures/meshes look wrong, check file conflicts\n")
            f.write("   - Use a mod manager for easier installation\n")
            f.write("   - Check the build log for processing details\n")
            f.write("   - BSA/BA2 files load faster and reduce game stuttering\n")

    def _generate_clean_summary(self,
                               summary_path: str,
                               mod_name: str,
                               package_info: Dict[str, Any]):
        """Generate a clean summary of what was created."""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"PACKAGE SUMMARY - {mod_name}\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Created: {package_info.get('created', 'Unknown')}\n")
            f.write(f"Game Type: {package_info.get('game_type', 'Unknown').title()}\n\n")

            components = package_info.get("components", {})
            
            if "packed" in components:
                packed = components["packed"]
                f.write("PACKED ARCHIVE (BSA/BA2 + ESP):\n")
                f.write(f"  File: {os.path.basename(packed['path'])}\n")
                f.write(f"  Contains: {packed['file_count']} game files\n")
                f.write(f"  Purpose: {packed['contains']}\n\n")

            if "loose" in components:
                loose = components["loose"]
                f.write("LOOSE ARCHIVE (Override Files):\n")
                f.write(f"  File: {os.path.basename(loose['path'])}\n")
                f.write(f"  Contains: {loose['file_count']} override files\n")
                f.write(f"  Purpose: {loose['contains']}\n\n")

            f.write("INSTALLATION ORDER:\n")
            f.write("1. Install packed archive first (BSA + ESP)\n")
            f.write("2. Install loose archive second (overrides)\n")
            f.write("3. Enable ESP in mod manager\n")

    def _generate_installation_instructions(self,
                                           instructions_path: str,
                                           mod_name: str,
                                           package_info: Dict[str, Any]):
        """Generate installation instructions."""

        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(f"INSTALLATION INSTRUCTIONS - {mod_name}\\n")
            f.write("=" * 50 + "\\n\\n")

            f.write("This package was created by Safe Resource Packer\\n")
            f.write("It contains optimized archives and loose override files.\\n\\n")

            # ESP + Archive installation
            if "esp" in package_info["components"] and "archive" in package_info["components"]:
                esp_name = os.path.basename(package_info["components"]["esp"]["path"])
                archive_name = os.path.basename(package_info["components"]["archive"]["path"])

                f.write("MAIN MOD INSTALLATION:\\n")
                f.write(f"1. Install {esp_name} and {archive_name} as a normal mod\\n")
                f.write("   - These files should be installed together\\n")
                f.write(f"   - The ESP will automatically load the {archive_name.split('.')[-1].upper()} archive\\n\\n")

            # Loose files installation
            if "loose_archive" in package_info["components"]:
                loose_name = os.path.basename(package_info["components"]["loose_archive"]["path"])

                f.write("LOOSE FILES (OVERRIDES):\\n")
                f.write(f"2. Extract and install {loose_name} separately\\n")
                f.write("   - These files MUST override the main mod\\n")
                f.write("   - Install with higher priority than the main mod\\n")
                f.write("   - These are critical overrides that cannot be packed\\n\\n")

            f.write("LOAD ORDER:\\n")
            f.write("- Main mod (ESP + archive) should load normally\\n")
            f.write("- Loose files should have higher priority in your mod manager\\n\\n")

            f.write("PERFORMANCE NOTES:\\n")
            f.write("- The archive contains optimized assets for better game performance\\n")
            f.write("- Loose files are kept separate to prevent mod conflicts\\n")
            f.write("- This setup provides the best balance of performance and compatibility\\n\\n")

            f.write("For questions or issues, refer to Safe Resource Packer documentation.\\n")

    def _generate_file_manifest(self,
                               manifest_path: str,
                               package_info: Dict[str, Any]):
        """Generate file manifest."""

        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write("FILE MANIFEST\\n")
            f.write("=" * 30 + "\\n\\n")

            for component_name, component_info in package_info["components"].items():
                f.write(f"{component_name.upper()}:\\n")

                if "file_count" in component_info:
                    f.write(f"  File Count: {component_info['file_count']}\\n")

                if "info" in component_info and "size_mb" in component_info["info"]:
                    f.write(f"  Size: {component_info['info']['size_mb']} MB\\n")

                f.write(f"  Path: {os.path.basename(component_info['path'])}\\n\\n")

    def _log_build_step(self, message: str, is_error: bool = False):
        """Log a build step."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        self.build_log.append(log_entry)

        if is_error:
            log(message, log_type='ERROR')
        else:
            log(message, log_type='INFO')

    def add_esp_template(self, template_path: str, game_type: str) -> bool:
        """
        Add ESP template for package building.

        Args:
            template_path: Path to ESP template file
            game_type: Game type for template

        Returns:
            Success status
        """
        return self.esp_manager.add_template(template_path, game_type)

    def get_build_summary(self) -> Dict[str, Any]:
        """Get summary of the build process."""
        return {
            "game_type": self.game_type,
            "compression_level": self.compression_level,
            "build_log": self.build_log.copy(),
            "package_info": self.package_info.copy()
        }


