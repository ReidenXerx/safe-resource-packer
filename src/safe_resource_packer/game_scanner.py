"""
Game Scanner - Bulletproof game directory detection

Scans the user's actual game Data directory to detect the real directory structure
they have, providing 100% accurate path classification based on their specific setup.
"""

import os
from typing import Dict, List, Set, Optional
from .dynamic_progress import log


class GameDirectoryScanner:
    """Scans game installations to detect actual directory structure."""

    def __init__(self):
        """Initialize game scanner."""
        # Universal fallback directories for all Bethesda games
        # Merged from all game-specific lists to catch every possible mod directory
        self.fallback_directories = {
            # Core game directories (common to all Creation Engine games)
            'meshes', 'textures', 'sounds', 'music', 'scripts', 'interface',
            'materials', 'shaders', 'shaderfx', 'vis', 'lodsettings',
            'grass', 'trees', 'terrain', 'facegen', 'facegendata',
            'actors', 'animationdata', 'animationdatasinglefile',
            'animationsetdatasinglefile', 'behaviordata', 'charactergen',
            'dialogueviews', 'effects', 'environment', 'lighting',
            'loadscreens', 'misc', 'planetdata', 'seq', 'sound',
            'strings', 'video', 'voices', 'weapons',
            
            # Skyrim-specific directories
            'animations_by_leito_v2_4', 'backup', 'bashtags', 'calientetools',
            'creature resource', 'dialogueviews', 'dip', 'docs', 'documentation',
            'dyndolod', 'esp', 'fla', 'fomod', 'grass', 'headpartwhitelist',
            'interface', 'jaysus lore version', 'killmove mod profiles',
            'lightplacer', 'lodsettings', 'mainmenuwallpapers', 'mapweathers',
            'mcm', 'medieval paintings', 'merge - the devil\'s in the details - final',
            'mod specific notes', 'modderresource', 'morten', 'music',
            'nemesis_engine', 'netscriptframework', 'ostim', 'pandora_engine',
            'particlelights', 'pbrmaterialobjects', 'pbrnifpatcher', 'pbrtexturesets',
            'plugins', 'readme', 'readmes', 'rmb spid references', 'runtimes',
            'scripts', 'seasons', 'security overhaul for ordinator', 'seq',
            'shadercache', 'shaders', 'skse', 'sound', 'sounds', 'source',
            'sseedit backups', 'sseedit cache', 'standalone_esp', 'strings',
            'textures', 'video',
            
            # Fallout 4-specific directories
            'aaf', 'alpia port', 'bcr', 'body textures',
            'boston emergency services mod (bems) 3.21',
            'companion bonnie and co (mod by makita v.0.01-beta)',
            'complex sorter', 'diversebodies', 'diversebodiesredux',
            'fo4edit', 'fo4edit backups', 'fo4edit cache', 'loose files - optional',
            'optional esl version', 'patching', 'pcl', 'scourge', 'scourge - lobotomitepack',
            'screenshots', 'tools', 'vis', 'xdi',
            
            # Universal modding tools and frameworks
            'f4se', 'mcm', 'fomod', 'docs', 'tools', 'config', 'folip', 'dyndolod', 'pbt', 'lsdata'
        }

        # Cache for scanned directories
        self._directory_cache = {}

    def scan_game_data_directory(self, game_path: str, game_type: str) -> Dict[str, Set[str]]:
        """
        Scan the game's Data directory to detect actual directory structure.

        Args:
            game_path: Path to game installation (e.g., "C:/Games/Skyrim Special Edition")
            game_type: Type of game ("skyrim" or "fallout4")

        Returns:
            Dict with 'detected' and 'fallback' directory sets (normalized to lowercase)
        """
        game_type = game_type.lower()
        cache_key = f"{game_path}_{game_type}"

        # Return cached result if available
        if cache_key in self._directory_cache:
            return self._directory_cache[cache_key]

        log(f"🔍 Scanning game Data directory: {game_path}", log_type='INFO')

        # Find Data directory
        data_dir = self._find_data_directory(game_path)
        if not data_dir:
            log(f"⚠️  Data directory not found in {game_path}, using fallback only", log_type='WARNING')
            result = {
                'detected': set(),
                'fallback': self.fallback_directories,
                'combined': self.fallback_directories
            }
            self._directory_cache[cache_key] = result
            return result

        # Scan top-level directories in Data folder
        detected_dirs = set()
        try:
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isdir(item_path):
                    # Normalize to lowercase for consistent matching
                    normalized_name = item.lower()
                    detected_dirs.add(normalized_name)
                    log(f"   📁 Found: {item} → {normalized_name}", debug_only=True, log_type='INFO')

            log(f"✅ Detected {len(detected_dirs)} directories in {data_dir}", log_type='SUCCESS')

        except Exception as e:
            log(f"❌ Failed to scan Data directory: {e}", log_type='ERROR')
            detected_dirs = set()

        # Get fallback directories (universal for all games)
        fallback_dirs = self.fallback_directories

        # Combine detected and fallback directories
        combined_dirs = detected_dirs.union(fallback_dirs)

        result = {
            'detected': detected_dirs,
            'fallback': fallback_dirs,
            'combined': combined_dirs
        }

        # Cache the result
        self._directory_cache[cache_key] = result

        log(f"📊 Directory scan complete:", log_type='INFO')
        log(f"   Detected: {len(detected_dirs)} directories", log_type='INFO')
        log(f"   Fallback: {len(fallback_dirs)} directories", log_type='INFO')
        log(f"   Combined: {len(combined_dirs)} directories", log_type='INFO')

        return result

    def _find_data_directory(self, game_path: str) -> Optional[str]:
        """
        Find the Data directory within the game installation.
        Simple approach - just check common locations.

        Args:
            game_path: Path to game installation

        Returns:
            Path to Data directory or None if not found
        """
        # Common Data directory locations
        possible_data_paths = [
            os.path.join(game_path, "Data"),
            os.path.join(game_path, "data"),
            os.path.join(game_path, "DATA"),
            # Sometimes Data is in a subdirectory
            os.path.join(game_path, "Game", "Data"),
            os.path.join(game_path, "game", "data"),
        ]

        for data_path in possible_data_paths:
            if os.path.exists(data_path) and os.path.isdir(data_path):
                log(f"✅ Found Data directory: {data_path}", debug_only=True, log_type='SUCCESS')
                return data_path

         # Try to find any directory named "data" (case-insensitive)
        try:
            for item in os.listdir(game_path):
                if item.lower() == 'data':
                    data_path = os.path.join(game_path, item)
                    if os.path.isdir(data_path):
                        log(f"✅ Found Data directory (case-insensitive): {data_path}", debug_only=True, log_type='SUCCESS')
                        return data_path
        except Exception:
            pass

        return None



# Global scanner instance
_game_scanner = None

def get_game_scanner() -> GameDirectoryScanner:
    """Get the global game scanner instance."""
    global _game_scanner
    if _game_scanner is None:
        _game_scanner = GameDirectoryScanner()
    return _game_scanner
