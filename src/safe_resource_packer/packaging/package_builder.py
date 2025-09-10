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
                 compression_level: int = 5,
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

        return True, package_info

    def _create_packed_archive(self, pack_files: List[str], mod_name: str, 
                              output_dir: str, package_info: Dict[str, Any],
                              esp_name: str = None, archive_name: str = None) -> bool:
        """Create BSA/BA2 + ESP archive for packed files."""
        # Set defaults
        esp_name = esp_name or mod_name
        archive_name = archive_name or mod_name
        
        self._log_build_step("Creating BSA/BA2 + ESP package")
        
        # 1. Create BSA/BA2 archive
        archive_path = os.path.join(output_dir, archive_name)
        log(f"Creating BSA at: {archive_path}", log_type='DEBUG')
        success, message = self.archive_creator.create_archive(
            pack_files, archive_path, archive_name
        )
        
        if not success:
            log(f"BSA/BA2 creation failed: {message}", log_type='ERROR')
            return False
        
        # Verify BSA was created and has reasonable size
        if os.path.exists(archive_path):
            bsa_size = os.path.getsize(archive_path)
            log(f"BSA created successfully: {archive_path} ({bsa_size} bytes, {bsa_size / 1024:.1f} KB)", log_type='INFO')
        else:
            log(f"ERROR: BSA file not found at expected path: {archive_path}", log_type='ERROR')
            return False
        
        # 2. Create ESP file
        esp_success, esp_path = self.esp_manager.create_esp(
            mod_name, output_dir, self.game_type, [archive_path]
        )
        
        if not esp_success:
            log(f"ESP creation failed: {esp_path}", log_type='ERROR')
            return False
        
        # Verify ESP was created
        if os.path.exists(esp_path):
            esp_size = os.path.getsize(esp_path)
            log(f"ESP created successfully: {esp_path} ({esp_size} bytes)", log_type='INFO')
        else:
            log(f"ERROR: ESP file not found at expected path: {esp_path}", log_type='ERROR')
            return False
        
        # 3. Compress both files to final archive
        final_files = [archive_path, esp_path]
        final_archive = os.path.join(output_dir, f"{mod_name}_Packed.7z")
        
        # Use compress_directory_with_folder_name to create proper structure
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mod_folder = os.path.join(temp_dir, f"{mod_name}_Packed")
            os.makedirs(mod_folder, exist_ok=True)
            
            # Copy BSA and ESP files to mod folder
            log(f"Files to copy: {final_files}", log_type='DEBUG')
            for file_path in final_files:
                log(f"Checking file: {file_path}", log_type='DEBUG')
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    log(f"File exists, size: {file_size} bytes ({file_size / 1024:.1f} KB)", log_type='DEBUG')
                    dst_path = os.path.join(mod_folder, os.path.basename(file_path))
                    shutil.copy2(file_path, dst_path)
                    log(f"Copied {os.path.basename(file_path)} to temp folder", log_type='DEBUG')
                else:
                    log(f"ERROR: File not found: {file_path}", log_type='ERROR')
            
            # Compress the mod folder
            compress_success, message = self.compressor.compress_directory_with_folder_name(
                mod_folder, final_archive, f"{mod_name}_Packed"
            )
        
        if compress_success:
            # Clean up individual files after successful compression
            try:
                if os.path.exists(archive_path):
                    os.remove(archive_path)
                    log(f"Cleaned up BSA/BA2: {os.path.basename(archive_path)}", log_type='INFO')
                if os.path.exists(esp_path):
                    os.remove(esp_path)
                    log(f"Cleaned up ESP: {os.path.basename(esp_path)}", log_type='INFO')
            except Exception as cleanup_error:
                log(f"Warning: Could not clean up individual files: {cleanup_error}", log_type='WARNING')
            
            package_info["components"]["packed"] = {
                "path": final_archive,
                "file_count": len(final_files),
                "contains": "BSA/BA2 + ESP"
            }
            self._log_build_step(f"Packed archive created: {os.path.basename(final_archive)}")
            return True
        else:
            log(f"Packed archive compression failed: {message}", log_type='ERROR')
            return False

    def _create_loose_archive(self, loose_files: List[str], mod_name: str,
                             output_dir: str, package_info: Dict[str, Any], options: Dict[str, Any] = None) -> bool:
        """Create 7z archive for loose files."""
        self._log_build_step("Creating loose files 7z archive")
        
        loose_archive = os.path.join(output_dir, f"{mod_name}_Loose.7z")
        
        # Simple approach: compress the loose folder contents directly
        if loose_files:
            # Use the user-defined loose folder from options, not the common path of files
            loose_folder = options.get('output_loose')
            if not loose_folder:
                # Fallback: use common path of loose files
                loose_folder = os.path.commonpath(loose_files)
                log(f"⚠️ No output_loose in options, using common path: {loose_folder}", log_type='WARNING')
            else:
                log(f"Using user-defined loose folder: {loose_folder}", log_type='DEBUG')
            
            # Use compress_directory_with_folder_name with the loose folder
            success, message = self.compressor.compress_directory_with_folder_name(
                loose_folder,
                loose_archive,
                f"{mod_name}_Loose"
            )
        else:
            success, message = False, "No loose files found"
        
        if success:
            package_info["components"]["loose"] = {
                "path": loose_archive,
                "file_count": len(loose_files),
                "contains": "Override files"
            }
            self._log_build_step(f"Loose archive created: {os.path.basename(loose_archive)}")
            return True
        else:
            log(f"Loose archive creation failed: {message}", log_type='ERROR')
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


