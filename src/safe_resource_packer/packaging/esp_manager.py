"""
ESP Manager - Template ESP handling and renaming

Manages template ESP files, handles renaming and BSA/BA2 references.
Uses user-provided template ESP files for maximum compatibility.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from ..dynamic_progress import log


class ESPManager:
    """Manages ESP template files and creates mod-specific ESP files."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize ESP manager.

        Args:
            template_dir: Directory containing template ESP files
        """
        self.template_dir = template_dir or self._get_default_template_dir()
        self.templates = {}
        self._load_templates()

    def _get_default_template_dir(self) -> str:
        """Get default template directory path."""
        # Templates will be stored alongside the package
        package_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(package_dir, "templates", "esp")

    def _load_templates(self):
        """Load available ESP templates."""
        if not os.path.exists(self.template_dir):
            log(f"Template directory not found: {self.template_dir}", log_type='WARNING')
            return

        for file in os.listdir(self.template_dir):
            if file.lower().endswith('.esp'):
                game_type = self._detect_game_type(file)
                self.templates[game_type] = os.path.join(self.template_dir, file)
                log(f"Loaded {game_type} ESP template: {file}", log_type='INFO')

    def _detect_game_type(self, filename: str) -> str:
        """Detect game type from ESP filename."""
        filename_lower = filename.lower()

        if 'fallout4' in filename_lower or 'fo4' in filename_lower:
            return 'fallout4'
        elif 'skyrim' in filename_lower or 'tes5' in filename_lower:
            return 'skyrim'
        else:
            # Default to Skyrim if unclear
            return 'skyrim'

    def create_esp(self,
                   mod_name: str,
                   output_path: str,
                   game_type: str = "skyrim",
                   bsa_files: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        Create ESP file for mod using template.

        Args:
            mod_name: Name of the mod (used for ESP filename)
            output_path: Directory where ESP should be created
            game_type: Target game ("skyrim" or "fallout4")
            bsa_files: List of BSA/BA2 files to reference (optional)

        Returns:
            Tuple of (success: bool, esp_path: str)
        """
        game_type = game_type.lower()

        # Get template path
        template_path = self.templates.get(game_type)
        if not template_path or not os.path.exists(template_path):
            return False, f"No template found for {game_type}"

        # Create output ESP path
        esp_filename = f"{mod_name}.esp"
        esp_path = os.path.join(output_path, esp_filename)

        try:
            # Handle BSA files (including chunked archives)
            if bsa_files:
                # Filter out non-existent files
                existing_bsa_files = [f for f in bsa_files if os.path.exists(f)]
                
                if len(existing_bsa_files) != len(bsa_files):
                    missing_files = [f for f in bsa_files if not os.path.exists(f)]
                    log(f"⚠️ Some BSA files not found: {missing_files}", log_type='WARNING')
                
                # Create ESP files for each BSA file
                created_esp_files = []
                
                # Separate texture archives from main archives
                texture_archives = [f for f in existing_bsa_files if 'textures' in os.path.basename(f).lower()]
                main_archives = [f for f in existing_bsa_files if 'textures' not in os.path.basename(f).lower()]
                
                if len(main_archives) == 1:
                    # Single main archive (with or without textures) - create one ESP with mod name
                    shutil.copy2(template_path, esp_path)
                    created_esp_files.append(esp_path)
                    log(f"📄 ESP created for main archive: {os.path.basename(main_archives[0])}", log_type='INFO')
                    if texture_archives:
                        log(f"📄 Note: {len(texture_archives)} texture archive(s) will be loaded automatically", log_type='INFO')
                elif len(main_archives) > 1:
                    # Multiple main archives (chunked) - create matching ESP files
                    log(f"📄 Creating {len(main_archives)} ESP files for chunked main archives:", log_type='INFO')
                    
                    for i, bsa_file in enumerate(main_archives):
                        file_size = os.path.getsize(bsa_file)
                        bsa_basename = os.path.basename(bsa_file)
                        log(f"  • {bsa_basename} ({file_size / (1024*1024):.1f} MB)", log_type='INFO')
                        
                        # Create ESP filename based on mod name, not BSA filename
                        # For chunked archives, create ESPs with mod name + chunk number
                        if 'pack.' in bsa_basename.lower():
                            # Extract chunk number from BSA filename like "modname_pack.pack.0.bsa"
                            parts = bsa_basename.split('.')
                            if len(parts) >= 3 and parts[-2].isdigit():
                                chunk_num = parts[-2]
                                chunk_esp_filename = f"{mod_name}_{chunk_num}.esp"
                            else:
                                chunk_esp_filename = f"{mod_name}.esp"
                        else:
                            # Non-chunked archive
                            chunk_esp_filename = f"{mod_name}.esp"
                        chunk_esp_path = os.path.join(output_path, chunk_esp_filename)
                        
                        # Copy template to create matching ESP
                        shutil.copy2(template_path, chunk_esp_path)
                        created_esp_files.append(chunk_esp_path)
                        log(f"📄 Created matching ESP: {chunk_esp_filename}", log_type='DEBUG')
                    
                    if texture_archives:
                        log(f"📄 Note: {len(texture_archives)} texture archive(s) will be loaded automatically", log_type='INFO')
                    
                    # Check if this looks like CAO-style chunking
                    chunked_names = [os.path.basename(f) for f in main_archives]
                    if any('pack' in name.lower() for name in chunked_names):
                        log(f"📦 Detected CAO-style chunked archives - created {len(created_esp_files)} matching ESP files", log_type='INFO')
                else:
                    # Only texture archives (no main archives) - create single ESP
                    shutil.copy2(template_path, esp_path)
                    created_esp_files.append(esp_path)
                    log(f"📄 ESP created for texture-only mod: {len(texture_archives)} texture archive(s)", log_type='INFO')
                
                # Return the first ESP file as the main one (for compatibility)
                return True, created_esp_files[0] if created_esp_files else esp_path
            else:
                # No BSA files - create single ESP with mod name
                shutil.copy2(template_path, esp_path)
                log(f"Created ESP: {esp_path}", log_type='SUCCESS')
                return True, esp_path

        except Exception as e:
            log(f"Failed to create ESP: {e}", log_type='ERROR')
            return False, str(e)

    def add_template(self, template_path: str, game_type: str) -> bool:
        """
        Add a new ESP template.

        Args:
            template_path: Path to the template ESP file
            game_type: Game type for this template

        Returns:
            Success status
        """
        if not os.path.exists(template_path):
            log(f"Template file not found: {template_path}", log_type='ERROR')
            return False

        if not template_path.lower().endswith('.esp'):
            log(f"Template must be an ESP file: {template_path}", log_type='ERROR')
            return False

        try:
            # Ensure template directory exists
            os.makedirs(self.template_dir, exist_ok=True)

            # Copy template to template directory
            template_filename = f"{game_type}_template.esp"
            dest_path = os.path.join(self.template_dir, template_filename)

            shutil.copy2(template_path, dest_path)

            # Update templates dict
            self.templates[game_type] = dest_path

            log(f"Added {game_type} template: {dest_path}", log_type='SUCCESS')
            return True

        except Exception as e:
            log(f"Failed to add template: {e}", log_type='ERROR')
            return False

    def list_templates(self) -> Dict[str, str]:
        """
        List available ESP templates.

        Returns:
            Dictionary of game_type -> template_path
        """
        return self.templates.copy()

    def validate_esp(self, esp_path: str) -> tuple[bool, str]:
        """
        Validate ESP file.

        Args:
            esp_path: Path to ESP file to validate

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not os.path.exists(esp_path):
            return False, "ESP file does not exist"

        if not esp_path.lower().endswith('.esp'):
            return False, "File is not an ESP file"

        # Basic file size check
        size = os.path.getsize(esp_path)
        if size < 100:  # ESP files should be at least 100 bytes
            return False, "ESP file appears to be too small"

        if size > 100 * 1024 * 1024:  # 100MB seems excessive for most ESPs
            return False, "ESP file appears to be unusually large"

        # Try to read first few bytes to check for ESP header
        try:
            with open(esp_path, 'rb') as f:
                header = f.read(4)
                if header != b'TES4' and header != b'TES5':
                    return False, "Invalid ESP header format"
        except Exception as e:
            return False, f"Could not read ESP file: {e}"

        return True, "ESP file appears valid"

    def get_esp_info(self, esp_path: str) -> Dict[str, any]:
        """
        Get information about ESP file.

        Args:
            esp_path: Path to ESP file

        Returns:
            Dictionary with ESP information
        """
        if not os.path.exists(esp_path):
            return {"exists": False}

        stat = os.stat(esp_path)
        is_valid, validation_msg = self.validate_esp(esp_path)

        info = {
            "exists": True,
            "size": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "valid": is_valid,
            "validation_message": validation_msg,
            "filename": os.path.basename(esp_path)
        }

        # Try to extract basic ESP information
        try:
            with open(esp_path, 'rb') as f:
                header = f.read(4)
                if header in [b'TES4', b'TES5']:
                    info["format"] = header.decode('ascii')
                    # Could extract more information here if needed
        except:
            pass

        return info

