"""
Package Builder - Complete mod packaging automation

Orchestrates the complete packaging pipeline from classification to final distribution package.
Creates BSA/BA2 archives, ESP files, compressed loose files, and final 7z packages.
"""

import os
import json
import shutil
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
            
            # Copy blacklisted files from the blacklisted directory (consistent with loose archive approach)
            blacklisted_dir = options.get('output_blacklisted')
            if blacklisted_dir and os.path.exists(blacklisted_dir):
                log(f"🚫 Copying blacklisted files from: {blacklisted_dir}", log_type='INFO')
                for item in os.listdir(blacklisted_dir):
                    item_path = os.path.join(blacklisted_dir, item)
                    dest_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
                        blacklisted_items_count += 1
                        log(f"📦 Added blacklisted folder: {item}", log_type='INFO')
                    elif os.path.isfile(item_path):
                        shutil.copy2(item_path, dest_path)
                        blacklisted_items_count += 1
                        log(f"📄 Added blacklisted file: {item}", log_type='INFO')
                
                if blacklisted_items_count == 0:
                    log(f"⚠️ No blacklisted items found in directory: {blacklisted_dir}", log_type='WARNING')
                    return False
            else:
                log(f"❌ Blacklisted directory not found: {blacklisted_dir}", log_type='ERROR')
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
        """Create BSA/BA2 + ESP archive for packed files with chunking support."""
        # Set defaults
        esp_name = esp_name or mod_name
        archive_name = archive_name or mod_name
        
        self._log_build_step("Creating BSA/BA2 + ESP package")
        
        # 1. Create BSA/BA2 archive(s) with chunking support
        bsa_file_path = os.path.join(output_dir, archive_name)
        log(f"Creating BSA at: {bsa_file_path}", log_type='DEBUG')
        
        # Use ArchiveCreator with chunking support (includes fallback methods)
        bsa_creation_success, bsa_creation_message = self.archive_creator.create_archive(
            pack_files, bsa_file_path, archive_name
        )
        
        if not bsa_creation_success:
            log(f"BSA/BA2 creation failed: {bsa_creation_message}", log_type='ERROR')
            return False
        
        # Find all created archive files (may be multiple chunks or single archive)
        archive_ext = ".ba2" if self.game_type == "fallout4" else ".bsa"
        
        created_archives = []
        
        # Look for BSA/BA2 files only (no ZIP fallback - ZIP is not a valid game archive format)
        for file in os.listdir(output_dir):
            if file.startswith(archive_name) and file.endswith(archive_ext):
                file_path = os.path.join(output_dir, file)
                if os.path.exists(file_path):
                    created_archives.append(file_path)
        
        if not created_archives:
            return False, f"No archive files found for {archive_name}"
        
        # Log created archives
        if len(created_archives) == 1:
            archive_size = os.path.getsize(created_archives[0])
            log(f"✅ BSA created: {os.path.basename(created_archives[0])} ({archive_size / (1024*1024):.1f} MB)", log_type='SUCCESS')
        else:
            log(f"✅ Created {len(created_archives)} chunked archives:", log_type='SUCCESS')
            total_size = 0
            for archive_path in created_archives:
                size = os.path.getsize(archive_path)
                total_size += size
                log(f"  • {os.path.basename(archive_path)} ({size / (1024*1024):.1f} MB)", log_type='SUCCESS')
            log(f"📊 Total chunked size: {total_size / (1024*1024):.1f} MB", log_type='INFO')
        
        # 2. Create ESP file(s) for all archives
        esp_creation_success, esp_file_path = self.esp_manager.create_esp(
            mod_name, output_dir, self.game_type, created_archives
        )
        
        if not esp_creation_success:
            log(f"ESP creation failed: {esp_file_path}", log_type='ERROR')
            return False
        
        # Find all ESP files that were created (may be multiple for chunked archives)
        esp_files = []
        if len(created_archives) == 1:
            # Single archive - should have one ESP with mod name
            if os.path.exists(esp_file_path):
                esp_files.append(esp_file_path)
                esp_file_size = os.path.getsize(esp_file_path)
                log(f"✅ ESP created: {os.path.basename(esp_file_path)} ({esp_file_size} bytes)", log_type='SUCCESS')
            else:
                log(f"ERROR: ESP file not found: {esp_file_path}", log_type='ERROR')
                return False
        else:
            # Multiple archives (chunked) - find all matching ESP files
            for archive_path in created_archives:
                archive_basename = os.path.basename(archive_path)
                archive_name_without_ext = os.path.splitext(archive_basename)[0]
                esp_filename = f"{archive_name_without_ext}.esp"
                esp_path = os.path.join(output_dir, esp_filename)
                
                if os.path.exists(esp_path):
                    esp_files.append(esp_path)
                    esp_file_size = os.path.getsize(esp_path)
                    log(f"✅ ESP created: {esp_filename} ({esp_file_size} bytes)", log_type='SUCCESS')
                else:
                    log(f"ERROR: ESP file not found: {esp_path}", log_type='ERROR')
                    return False
            
            log(f"📄 Created {len(esp_files)} ESP files for chunked archives", log_type='INFO')
        
        # 3. Compress all files to final 7z archive
        files_to_compress = created_archives + esp_files
        packed_7z_path = os.path.join(output_dir, f"{mod_name}_Packed.7z")
        
        # Use compress_directory_with_folder_name to create proper structure
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            mod_folder = os.path.join(temp_dir, f"{mod_name}_Packed")
            os.makedirs(mod_folder, exist_ok=True)
            
            # Copy all BSA and ESP files to mod folder
            log(f"📦 Copying {len(files_to_compress)} files to package", log_type='INFO')
            for file_path in files_to_compress:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    dst_path = os.path.join(mod_folder, os.path.basename(file_path))
                    shutil.copy2(file_path, dst_path)
                    log(f"  • {os.path.basename(file_path)} ({file_size / (1024*1024):.1f} MB)", log_type='DEBUG')
                else:
                    log(f"ERROR: File not found: {file_path}", log_type='ERROR')
            
            # Compress the mod folder
            compression_success, compression_message = self.compressor.compress_directory_with_folder_name(
                mod_folder, packed_7z_path, f"{mod_name}_Packed"
            )
        
        if compression_success:
            # Clean up individual files after successful compression
            try:
                for file_path in files_to_compress:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        log(f"🧹 Cleaned up: {os.path.basename(file_path)}", log_type='DEBUG')
            except Exception as cleanup_error:
                log(f"Warning: Could not clean up individual files: {cleanup_error}", log_type='WARNING')
            
            package_info["components"]["pack"] = {
                "path": packed_7z_path,
                "file_count": len(files_to_compress),
                "contains": f"{len(created_archives)} BSA/BA2 chunks + ESP",
                "chunks": len(created_archives)
            }
            self._log_build_step(f"Packed archive created: {os.path.basename(packed_7z_path)}")
            return True
        else:
            log(f"Packed archive compression failed: {compression_message}", log_type='ERROR')
            return False


    def _create_loose_archive(self, loose_files: List[str], mod_name: str,
                             output_dir: str, package_info: Dict[str, Any], options: Dict[str, Any] = None) -> bool:
        """Create 7z archive for loose files (including blacklisted files)."""
        self._log_build_step("Creating loose files 7z archive")
        
        loose_7z_path = os.path.join(output_dir, f"{mod_name}_Loose.7z")
        
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
            
            # 2. Copy blacklisted files (if any)
            blacklisted_dir = options.get('output_blacklisted')
            if blacklisted_dir and os.path.exists(blacklisted_dir):
                log(f"🚫 Adding blacklisted files from: {blacklisted_dir}", log_type='DEBUG')
                for item in os.listdir(blacklisted_dir):
                    item_path = os.path.join(blacklisted_dir, item)
                    dest_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
                        blacklisted_items_count += 1
                        log(f"📦 Added blacklisted folder: {item}", log_type='DEBUG')
                    elif os.path.isfile(item_path):
                        shutil.copy2(item_path, dest_path)
                        blacklisted_items_count += 1
                        log(f"📄 Added blacklisted file: {item}", log_type='DEBUG')
                
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
                f.write("   - Extract the *_Loose.7z file\n")
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


