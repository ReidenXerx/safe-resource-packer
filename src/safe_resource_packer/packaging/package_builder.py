"""
Package Builder - Complete mod packaging automation

Orchestrates the complete packaging pipeline from classification to final distribution package.
Creates BSA/BA2 archives, ESP files, compressed loose files, and final 7z packages.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from ..utils import log
from .archive_creator import ArchiveCreator
from .esp_manager import ESPManager
from .compressor import Compressor


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
                              options: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Build complete mod package from classification results.

        Args:
            classification_results: Results from SafeResourcePacker classification
            mod_name: Name of the mod
            output_dir: Directory to create package in
            options: Additional options for package creation

        Returns:
            Tuple of (success: bool, package_path: str, package_info: dict)
        """
        options = options or {}
        self._log_build_step(f"Starting package build for '{mod_name}'")

        try:
            # Validate inputs
            if not self._validate_inputs(classification_results, mod_name, output_dir):
                return False, "", {}

            # Create package directory structure
            package_dir = self._create_package_structure(output_dir, mod_name)

            # Build package components
            success, package_info = self._build_package_components(
                classification_results, mod_name, package_dir, options
            )

            if not success:
                return False, "", {}

            # Generate package metadata BEFORE creating final package
            self._generate_package_metadata(package_dir, mod_name, package_info, options)

            # Create final compressed package
            final_package_path = self._create_final_package(package_dir, mod_name, options)

            self._log_build_step(f"Package build completed: {final_package_path}")

            return True, final_package_path, package_info

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

    def _create_package_structure(self, output_dir: str, mod_name: str) -> str:
        """Create package directory structure."""

        package_dir = os.path.join(output_dir, f"{mod_name}_Package")

        # Create directories
        dirs_to_create = [
            package_dir,
            os.path.join(package_dir, "archives"),
            os.path.join(package_dir, "loose"),
            os.path.join(package_dir, "esp"),
            os.path.join(package_dir, "_metadata")
        ]

        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)

        self._log_build_step(f"Created package structure: {package_dir}")
        return package_dir

    def _build_package_components(self,
                                 classification_results: Dict[str, List[str]],
                                 mod_name: str,
                                 package_dir: str,
                                 options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Build all package components."""

        package_info = {
            "mod_name": mod_name,
            "game_type": self.game_type,
            "created": datetime.now().isoformat(),
            "components": {}
        }

        # 1. Create BSA/BA2 archive from pack files
        if 'pack' in classification_results and classification_results['pack']:
            self._log_build_step("Creating BSA/BA2 archive from pack files")

            archive_name = f"{mod_name}"
            archive_path = os.path.join(package_dir, "archives", archive_name)

            success, archive_path = self.archive_creator.create_archive(
                classification_results['pack'],
                archive_path,
                mod_name,
                temp_dir=os.path.join(package_dir, "_temp_archive")
            )

            if success:
                package_info["components"]["archive"] = {
                    "path": archive_path,
                    "file_count": len(classification_results['pack']),
                    "info": self.archive_creator.get_archive_info(archive_path)
                }
                self._log_build_step(f"Archive created: {os.path.basename(archive_path)}")
            else:
                log(f"Archive creation failed: {archive_path}", log_type='ERROR')
                return False, {}

        # 2. Create ESP file
        self._log_build_step("Creating ESP file")

        esp_dir = os.path.join(package_dir, "esp")
        bsa_files = [package_info["components"]["archive"]["path"]] if "archive" in package_info["components"] else None

        esp_success, esp_path = self.esp_manager.create_esp(
            mod_name, esp_dir, self.game_type, bsa_files
        )

        if esp_success:
            package_info["components"]["esp"] = {
                "path": esp_path,
                "info": self.esp_manager.get_esp_info(esp_path)
            }
            self._log_build_step(f"ESP created: {os.path.basename(esp_path)}")
        else:
            log(f"ESP creation failed: {esp_path}", log_type='WARNING')
            # Continue without ESP - not critical

        # 3. Compress loose files
        if 'loose' in classification_results and classification_results['loose']:
            self._log_build_step("Compressing loose files")

            loose_archive_path = os.path.join(package_dir, "loose", f"{mod_name}_Loose.7z")

            success, message = self.compressor.compress_files(
                classification_results['loose'],
                loose_archive_path
            )

            if success:
                package_info["components"]["loose_archive"] = {
                    "path": loose_archive_path,
                    "file_count": len(classification_results['loose']),
                    "info": self.compressor.get_archive_info(loose_archive_path)
                }
                self._log_build_step(f"Loose files compressed: {os.path.basename(loose_archive_path)}")
            else:
                log(f"Loose file compression failed: {message}", log_type='ERROR')
                return False, {}

        return True, package_info

    def _create_final_package(self,
                             package_dir: str,
                             mod_name: str,
                             options: Dict[str, Any]) -> str:
        """Create final compressed package."""

        self._log_build_step("Creating final package")

        # Collect all files for final package
        final_files = []

        # Add ESP file (if exists)
        esp_dir = os.path.join(package_dir, "esp")
        if os.path.exists(esp_dir):
            for file in os.listdir(esp_dir):
                if file.endswith('.esp'):
                    final_files.append(os.path.join(esp_dir, file))

        # Add archive file (if exists)
        archives_dir = os.path.join(package_dir, "archives")
        if os.path.exists(archives_dir):
            for file in os.listdir(archives_dir):
                if file.endswith(('.bsa', '.ba2', '.zip')):  # Include ZIP fallback files
                    final_files.append(os.path.join(archives_dir, file))

        # Add loose files archive (if exists)
        loose_dir = os.path.join(package_dir, "loose")
        if os.path.exists(loose_dir):
            for file in os.listdir(loose_dir):
                if file.endswith(('.7z', '.zip')):  # Include ZIP fallback files
                    final_files.append(os.path.join(loose_dir, file))

        # Add metadata (if exists)
        metadata_dir = os.path.join(package_dir, "_metadata")
        if os.path.exists(metadata_dir):
            for file in os.listdir(metadata_dir):
                final_files.append(os.path.join(metadata_dir, file))

        # Create final package
        final_package_path = os.path.join(os.path.dirname(package_dir), f"{mod_name}_v1.0.7z")

        success, message = self.compressor.compress_files(
            final_files,
            final_package_path,
            package_dir
        )

        if success:
            self._log_build_step(f"Final package created: {os.path.basename(final_package_path)}")

            # Clean up temporary package directory if requested
            if options.get('cleanup_temp', True):
                try:
                    shutil.rmtree(package_dir)
                    self._log_build_step("Cleaned up temporary files")
                except:
                    log("Could not clean up temporary files", log_type='WARNING')
        else:
            log(f"Final package creation failed: {message}", log_type='ERROR')

        return final_package_path if success else ""

    def _generate_package_metadata(self,
                                  package_dir: str,
                                  mod_name: str,
                                  package_info: Dict[str, Any],
                                  options: Dict[str, Any]):
        """Generate package metadata files."""

        metadata_dir = os.path.join(package_dir, "_metadata")

        # Ensure metadata directory exists
        os.makedirs(metadata_dir, exist_ok=True)

        # 1. Package info JSON
        info_path = os.path.join(metadata_dir, "package_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, default=str)

        # 2. Installation instructions
        instructions_path = os.path.join(metadata_dir, "INSTALLATION.txt")
        self._generate_installation_instructions(instructions_path, mod_name, package_info)

        # 3. Build log
        log_path = os.path.join(metadata_dir, "build_log.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Build Log for {mod_name}\\n")
            f.write(f"Created: {datetime.now().isoformat()}\\n")
            f.write("=" * 50 + "\\n\\n")
            for entry in self.build_log:
                f.write(f"{entry}\\n")

        # 4. File manifest
        manifest_path = os.path.join(metadata_dir, "file_manifest.txt")
        self._generate_file_manifest(manifest_path, package_info)

        self._log_build_step("Generated package metadata")

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


