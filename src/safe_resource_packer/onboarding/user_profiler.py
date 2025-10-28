"""
User profiling system for personalized experiences.

This module manages user preferences, mod manager detection, and personalization
settings to provide tailored guidance and interface adaptations.
"""

import os
import platform
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import winreg
from ..dynamic_progress import log


class UserProfiler:
    """Manages user profiling and preference detection."""
    
    def __init__(self):
        """Initialize the user profiler."""
        self.system_info = self._get_system_info()
        self.config_file = Path.home() / '.safe_resource_packer' / 'user_profile.json'
        
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
    
    def detect_mod_managers(self) -> Dict[str, Optional[str]]:
        """
        Detect installed mod managers and their paths.
        
        Returns:
            Dictionary with mod manager names and their installation paths
        """
        detected = {
            'MO2': None,
            'Vortex': None,
            'NMM': None
        }
        
        if platform.system() == 'Windows':
            detected.update(self._detect_windows_mod_managers())
        else:
            # For Linux/macOS, check common Wine/Proton locations
            detected.update(self._detect_unix_mod_managers())
            
        return detected
    
    def _detect_windows_mod_managers(self) -> Dict[str, Optional[str]]:
        """Detect mod managers on Windows using registry and common paths."""
        detected = {}
        
        # Detect MO2
        mo2_path = self._find_mo2_installation()
        detected['MO2'] = mo2_path
        
        # Detect Vortex
        vortex_path = self._find_vortex_installation()
        detected['Vortex'] = vortex_path
        
        # Detect NMM (legacy)
        nmm_path = self._find_nmm_installation()
        detected['NMM'] = nmm_path
        
        return detected
    
    def _find_mo2_installation(self) -> Optional[str]:
        """Find Mod Organizer 2 installation path."""
        # Common MO2 installation paths
        common_paths = [
            Path.home() / "AppData/Local/ModOrganizer",
            Path("C:/Modding/MO2"),
            Path("C:/Games/MO2"),
            Path("C:/Program Files/Mod Organizer 2"),
            Path("C:/Program Files (x86)/Mod Organizer 2")
        ]
        
        for path in common_paths:
            if path.exists() and (path / "ModOrganizer.exe").exists():
                return str(path)
        
        # Try registry detection
        try:
            if platform.system() == 'Windows':
                import winreg
                # Check for MO2 in registry (if it was installed via installer)
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if "Mod Organizer" in display_name:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    if Path(install_location).exists():
                                        return install_location
                            except FileNotFoundError:
                                continue
        except ImportError:
            pass  # winreg not available on non-Windows
        except Exception:
            pass  # Registry access failed
            
        return None
    
    def _find_vortex_installation(self) -> Optional[str]:
        """Find Vortex installation path."""
        # Vortex is typically installed in AppData
        vortex_paths = [
            Path.home() / "AppData/Roaming/Vortex",
            Path("C:/Program Files/Black Tree Gaming Ltd/Vortex"),
            Path("C:/Program Files (x86)/Black Tree Gaming Ltd/Vortex")
        ]
        
        for path in vortex_paths:
            if path.exists():
                return str(path)
                
        return None
    
    def _find_nmm_installation(self) -> Optional[str]:
        """Find Nexus Mod Manager installation path (legacy)."""
        nmm_paths = [
            Path("C:/Program Files/Nexus Mod Manager"),
            Path("C:/Program Files (x86)/Nexus Mod Manager"),
            Path.home() / "AppData/Local/Black_Tree_Gaming"
        ]
        
        for path in nmm_paths:
            if path.exists():
                return str(path)
                
        return None
    
    def _detect_unix_mod_managers(self) -> Dict[str, Optional[str]]:
        """Detect mod managers on Linux/macOS (Wine/Proton)."""
        detected = {}
        
        # Check common Wine prefixes
        wine_prefixes = [
            Path.home() / ".wine",
            Path.home() / ".local/share/Steam/steamapps/compatdata"
        ]
        
        for prefix in wine_prefixes:
            if prefix.exists():
                # Look for MO2 in Wine prefix
                mo2_path = prefix / "drive_c/Modding/MO2"
                if mo2_path.exists():
                    detected['MO2'] = str(mo2_path)
                    
                # Look for Vortex in Wine prefix
                vortex_path = prefix / "drive_c/users" / os.getenv('USER', 'user') / "AppData/Roaming/Vortex"
                if vortex_path.exists():
                    detected['Vortex'] = str(vortex_path)
        
        return detected
    
    def detect_games(self, force_rescan: bool = False) -> Dict[str, Optional[str]]:
        """
        Detect installed games and their paths.
        
        Args:
            force_rescan: If True, ignore cached results and rescan system
        
        Returns:
            Dictionary with game names and their installation paths
        """
        # Check if we have cached game paths and they're recent (unless forcing rescan)
        if not force_rescan:
            cached_games = self.get_saved_game_paths()
            if cached_games:
                profile = self.load_user_profile()
                last_detected = profile.get('games_last_detected') or profile.get('games_last_updated')
                
                if last_detected:
                    try:
                        from datetime import datetime, timedelta
                        last_scan = datetime.fromisoformat(last_detected)
                        # Use cached results if less than 7 days old
                        if datetime.now() - last_scan < timedelta(days=7):
                            log(f"📋 Using cached game paths ({len(cached_games)} games)", log_type='INFO')
                            # Fill in None for games not found in cache
                            all_games = {
                                'Skyrim Special Edition': None,
                                'Skyrim Anniversary Edition': None,
                                'Fallout 4': None,
                                'Skyrim Legendary Edition': None,
                                'Fallout 76': None,
                                'Starfield': None
                            }
                            all_games.update(cached_games)
                            return all_games
                    except Exception:
                        pass  # Fall through to full detection
        
        # Run full detection
        detected_games = {}
        
        if platform.system() == 'Windows':
            detected_games.update(self._detect_windows_games())
        else:
            detected_games.update(self._detect_unix_games())
            
        return detected_games
    
    def _save_detected_games(self, games: Dict[str, Optional[str]]):
        """Save detected game paths to persistent config."""
        try:
            profile = self.load_user_profile()
            
            # Only save games that were actually found
            detected_games = {name: path for name, path in games.items() if path is not None}
            
            if detected_games:
                profile['detected_games'] = detected_games
                profile['games_last_detected'] = datetime.now().isoformat()
                self.save_user_preferences(profile)
                log(f"💾 Saved {len(detected_games)} game paths to config", log_type='INFO')
            
        except Exception as e:
            log(f"⚠️ Failed to save detected games: {e}", log_type='WARNING')
    
    def get_saved_game_paths(self) -> Dict[str, str]:
        """Get previously detected game paths from config."""
        try:
            profile = self.load_user_profile()
            return profile.get('detected_games', {})
        except Exception as e:
            log(f"⚠️ Failed to load saved game paths: {e}", log_type='WARNING')
            return {}
    
    def get_game_path(self, game_name: str) -> Optional[str]:
        """Get path for a specific game from config."""
        saved_games = self.get_saved_game_paths()
        return saved_games.get(game_name)
    
    def update_game_path(self, game_name: str, path: str):
        """Update or add a game path to the config."""
        try:
            profile = self.load_user_profile()
            
            if 'detected_games' not in profile:
                profile['detected_games'] = {}
            
            profile['detected_games'][game_name] = path
            profile['games_last_updated'] = datetime.now().isoformat()
            
            self.save_user_preferences(profile)
            log(f"💾 Updated {game_name} path: {path}", log_type='INFO')
            
        except Exception as e:
            log(f"⚠️ Failed to update game path: {e}", log_type='WARNING')
    
    @staticmethod
    def get_available_game_paths() -> Dict[str, str]:
        """
        Static method to get available game paths from anywhere in the application.
        
        Returns:
            Dictionary of available games and their paths
        """
        try:
            profiler = UserProfiler()
            return profiler.get_saved_game_paths()
        except Exception as e:
            log(f"⚠️ Failed to get game paths: {e}", log_type='WARNING')
            return {}
    
    @staticmethod
    def get_game_data_path(game_name: str) -> Optional[str]:
        """
        Static method to get a specific game's Data folder path.
        
        Args:
            game_name: Name of the game (e.g., 'Skyrim Special Edition')
            
        Returns:
            Path to the game's Data folder, or None if not found
        """
        try:
            profiler = UserProfiler()
            game_path = profiler.get_game_path(game_name)
            if game_path:
                from pathlib import Path
                data_path = Path(game_path) / "Data"
                if data_path.exists():
                    return str(data_path)
        except Exception as e:
            log(f"⚠️ Failed to get game data path: {e}", log_type='WARNING')
        
        return None
    
    def _detect_windows_games(self) -> Dict[str, Optional[str]]:
        """Detect games on Windows using comprehensive system-wide search."""
        games = {
            'Skyrim Special Edition': None,
            'Skyrim Anniversary Edition': None,
            'Fallout 4': None,
            'Skyrim Legendary Edition': None,
            'Fallout 76': None,
            'Starfield': None
        }
        
        log("🔍 Starting comprehensive game detection...", log_type='INFO')
        
        # Step 1: Quick check - Steam and common paths (fast)
        log("  📋 Checking Steam and common paths...", log_type='INFO')
        steam_games = self._detect_steam_games()
        games.update(steam_games)
        
        common_games = self._detect_common_paths()
        for game, path in common_games.items():
            if games[game] is None:
                games[game] = path
        
        # Step 2: Registry check (Windows-specific, fast)
        log("  🗃️ Checking Windows registry...", log_type='INFO')
        registry_games = self._detect_registry_games()
        for game, path in registry_games.items():
            if games[game] is None:
                games[game] = path
        
        # Step 3: System-wide executable search (slower but comprehensive)
        missing_games = [name for name, path in games.items() if path is None]
        if missing_games:
            log(f"  🌐 Searching system-wide for {len(missing_games)} missing games...", log_type='INFO')
            system_games = self._detect_system_wide_games(missing_games)
            for game, path in system_games.items():
                if games[game] is None:
                    games[game] = path
        
        found_count = sum(1 for path in games.values() if path is not None)
        log(f"✅ Game detection complete: {found_count}/{len(games)} games found", log_type='INFO')
        
        # Save detected games to persistent config
        self._save_detected_games(games)
        
        return games
    
    def _detect_steam_games(self) -> Dict[str, Optional[str]]:
        """Detect Steam games using Steam's installation data."""
        games = {}
        
        # Common Steam installation paths
        steam_paths = [
            "C:/Program Files (x86)/Steam",
            "C:/Program Files/Steam",
            Path.home() / "Steam"
        ]
        
        for steam_path in steam_paths:
            steam_path = Path(steam_path)
            if steam_path.exists():
                # Look for steamapps/common
                common_path = steam_path / "steamapps/common"
                if common_path.exists():
                    # Check for specific games
                    game_folders = {
                        'Skyrim Special Edition': 'Skyrim Special Edition',
                        'Fallout 4': 'Fallout 4',
                        'Skyrim Legendary Edition': 'Skyrim'
                    }
                    
                    for game_name, folder_name in game_folders.items():
                        game_path = common_path / folder_name
                        if game_path.exists() and (game_path / "Data").exists():
                            games[game_name] = str(game_path)
        
        return games
    
    def _detect_common_paths(self) -> Dict[str, Optional[str]]:
        """Check common game installation paths."""
        games = {}
        
        # Common installation paths (expanded list)
        common_paths = {
            'Skyrim Special Edition': [
                "C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition",
                "C:/Program Files/Steam/steamapps/common/Skyrim Special Edition", 
                "C:/Games/Skyrim Special Edition",
                "D:/Games/Skyrim Special Edition",
                "E:/Games/Skyrim Special Edition",
                "C:/Program Files/Skyrim Special Edition",
                "C:/Program Files (x86)/Skyrim Special Edition"
            ],
            'Skyrim Anniversary Edition': [
                "C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition",
                "C:/Program Files/Steam/steamapps/common/Skyrim Special Edition",
                "C:/Games/Skyrim Special Edition", 
                "D:/Games/Skyrim Special Edition"
            ],
            'Fallout 4': [
                "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4",
                "C:/Program Files/Steam/steamapps/common/Fallout 4",
                "C:/Games/Fallout 4",
                "D:/Games/Fallout 4",
                "E:/Games/Fallout 4",
                "C:/Program Files/Fallout 4",
                "C:/Program Files (x86)/Fallout 4"
            ],
            'Skyrim Legendary Edition': [
                "C:/Program Files (x86)/Steam/steamapps/common/Skyrim",
                "C:/Program Files/Steam/steamapps/common/Skyrim",
                "C:/Games/Skyrim",
                "D:/Games/Skyrim"
            ],
            'Fallout 76': [
                "C:/Program Files (x86)/Steam/steamapps/common/Fallout76",
                "C:/Program Files/Steam/steamapps/common/Fallout76",
                "C:/Games/Fallout76",
                "D:/Games/Fallout76"
            ],
            'Starfield': [
                "C:/Program Files (x86)/Steam/steamapps/common/Starfield",
                "C:/Program Files/Steam/steamapps/common/Starfield",
                "C:/Games/Starfield",
                "D:/Games/Starfield"
            ]
        }
        
        for game, paths in common_paths.items():
            for path in paths:
                game_path = Path(path)
                if game_path.exists() and (game_path / "Data").exists():
                    games[game] = str(game_path)
                    log(f"    ✅ Found {game} at {path}", log_type='INFO')
                    break
        
        return games
    
    def _detect_registry_games(self) -> Dict[str, Optional[str]]:
        """Detect games using Windows registry entries."""
        games = {}
        
        try:
            import winreg
            
            # Registry paths where games might be registered
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            
            # Game identifiers to look for in registry
            game_identifiers = {
                'Skyrim Special Edition': ['skyrim special edition', 'skyrimse', 'tes v'],
                'Skyrim Anniversary Edition': ['skyrim anniversary', 'skyrim special edition'],
                'Fallout 4': ['fallout 4', 'fallout4'],
                'Skyrim Legendary Edition': ['skyrim', 'tes v', 'elder scrolls v'],
                'Fallout 76': ['fallout 76', 'fallout76'],
                'Starfield': ['starfield']
            }
            
            for hive, reg_path in registry_paths:
                try:
                    with winreg.OpenKey(hive, reg_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0].lower()
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        
                                        # Check if this matches any of our games
                                        for game_name, identifiers in game_identifiers.items():
                                            if games.get(game_name) is None:  # Only if not found yet
                                                for identifier in identifiers:
                                                    if identifier in display_name:
                                                        install_path = Path(install_location)
                                                        if install_path.exists() and (install_path / "Data").exists():
                                                            games[game_name] = str(install_path)
                                                            log(f"    ✅ Found {game_name} via registry at {install_location}", log_type='INFO')
                                                            break
                                                if games.get(game_name):
                                                    break
                                        
                                    except FileNotFoundError:
                                        pass  # Missing InstallLocation or DisplayName
                                i += 1
                            except OSError:
                                break  # No more subkeys
                except OSError:
                    continue  # Registry path doesn't exist
                    
        except ImportError:
            log("    ⚠️ Registry detection unavailable (winreg not available)", log_type='WARNING')
        except Exception as e:
            log(f"    ⚠️ Registry detection failed: {e}", log_type='WARNING')
        
        return games
    
    def _detect_system_wide_games(self, missing_games: list) -> Dict[str, Optional[str]]:
        """Search for game executables across the entire system."""
        games = {}
        
        # Game executable patterns
        game_executables = {
            'Skyrim Special Edition': ['SkyrimSE.exe', 'SkyrimSELauncher.exe'],
            'Skyrim Anniversary Edition': ['SkyrimSE.exe', 'SkyrimSELauncher.exe'],
            'Fallout 4': ['Fallout4.exe', 'Fallout4Launcher.exe'],
            'Skyrim Legendary Edition': ['TESV.exe', 'SkyrimLauncher.exe'],
            'Fallout 76': ['Fallout76.exe'],
            'Starfield': ['Starfield.exe']
        }
        
        # Get all drives to search
        drives = self._get_system_drives()
        log(f"    🔍 Searching drives: {', '.join(drives)}", log_type='INFO')
        
        for game_name in missing_games:
            if game_name not in game_executables:
                continue
                
            log(f"    🔍 Searching for {game_name}...", log_type='INFO')
            
            for drive in drives:
                for exe_name in game_executables[game_name]:
                    exe_path = self._find_executable_on_drive(drive, exe_name)
                    if exe_path:
                        game_dir = exe_path.parent
                        if (game_dir / "Data").exists():
                            games[game_name] = str(game_dir)
                            log(f"    ✅ Found {game_name} at {game_dir}", log_type='INFO')
                            break
                if games.get(game_name):
                    break
        
        return games
    
    def _get_system_drives(self) -> list:
        """Get list of available drives on Windows."""
        drives = []
        try:
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if Path(drive).exists():
                    drives.append(drive)
        except Exception as e:
            log(f"    ⚠️ Drive detection failed: {e}, using C:\\ only", log_type='WARNING')
            drives = ["C:\\"]
        
        return drives
    
    def _find_executable_on_drive(self, drive: str, exe_name: str) -> Optional[Path]:
        """Find an executable on a specific drive."""
        try:
            # Common game installation directories to prioritize
            priority_paths = [
                "Program Files (x86)\\Steam\\steamapps\\common",
                "Program Files\\Steam\\steamapps\\common", 
                "Games",
                "Steam\\steamapps\\common",
                "Epic Games",
                "GOG Galaxy\\Games",
                "Program Files (x86)",
                "Program Files"
            ]
            
            drive_path = Path(drive)
            
            # First, check priority paths (faster)
            for priority_path in priority_paths:
                search_path = drive_path / priority_path
                if search_path.exists():
                    try:
                        for root, dirs, files in os.walk(search_path):
                            if exe_name.lower() in [f.lower() for f in files]:
                                exe_path = Path(root) / exe_name
                                # Verify it's actually a game directory
                                if self._is_valid_game_directory(exe_path.parent):
                                    return exe_path
                            
                            # Limit depth to avoid going too deep
                            if len(Path(root).parts) - len(search_path.parts) > 3:
                                dirs.clear()  # Don't go deeper
                    except (OSError, PermissionError):
                        continue
            
            # If not found in priority paths, do a broader search (much slower)
            log(f"      🐌 Doing full drive search for {exe_name} on {drive} (this may take a while)...", log_type='INFO')
            try:
                for root, dirs, files in os.walk(drive_path):
                    # Skip system directories and other non-game locations
                    dirs[:] = [d for d in dirs if not d.lower().startswith(('windows', 'system', '$', 'programdata'))]
                    
                    if exe_name.lower() in [f.lower() for f in files]:
                        exe_path = Path(root) / exe_name
                        if self._is_valid_game_directory(exe_path.parent):
                            return exe_path
                    
                    # Limit depth for performance
                    if len(Path(root).parts) > 6:
                        dirs.clear()
                        
            except (OSError, PermissionError):
                pass
                
        except Exception as e:
            log(f"      ⚠️ Search failed on {drive}: {e}", log_type='WARNING')
        
        return None
    
    def _is_valid_game_directory(self, path: Path) -> bool:
        """Check if a directory looks like a valid game installation."""
        if not path.exists():
            return False
            
        # Must have Data directory
        if not (path / "Data").exists():
            return False
            
        # Should have some typical game files
        game_indicators = [
            'CreationKit.exe', 'Archive.exe', 'bsarch.exe',
            'steam_api64.dll', 'steam_api.dll',
            'Data'
        ]
        
        has_indicators = any((path / indicator).exists() for indicator in game_indicators)
        return has_indicators
    
    def _detect_unix_games(self) -> Dict[str, Optional[str]]:
        """Detect games on Linux/macOS (Steam/Proton)."""
        games = {}
        
        # Steam on Linux paths
        steam_paths = [
            Path.home() / ".steam/steam/steamapps/common",
            Path.home() / ".local/share/Steam/steamapps/common"
        ]
        
        for steam_path in steam_paths:
            if steam_path.exists():
                # Check for Proton games
                game_folders = {
                    'Skyrim Special Edition': 'Skyrim Special Edition',
                    'Fallout 4': 'Fallout 4'
                }
                
                for game_name, folder_name in game_folders.items():
                    game_path = steam_path / folder_name
                    if game_path.exists():
                        games[game_name] = str(game_path)
        
        return games
    
    def get_recommended_setup(self, detected_managers: Dict[str, Optional[str]], 
                            detected_games: Dict[str, Optional[str]]) -> Dict[str, str]:
        """
        Get recommended setup based on detected software.
        
        Args:
            detected_managers: Detected mod managers
            detected_games: Detected games
            
        Returns:
            Recommended setup configuration
        """
        recommendations = {
            'mod_manager': 'Manual',
            'primary_game': 'Unknown',
            'experience_level': 'beginner'
        }
        
        # Recommend mod manager based on what's installed
        if detected_managers.get('MO2'):
            recommendations['mod_manager'] = 'MO2'
            recommendations['experience_level'] = 'intermediate'
        elif detected_managers.get('Vortex'):
            recommendations['mod_manager'] = 'Vortex'
            recommendations['experience_level'] = 'beginner'
        elif detected_managers.get('NMM'):
            recommendations['mod_manager'] = 'NMM'
            recommendations['experience_level'] = 'beginner'
        
        # Recommend primary game
        game_priority = [
            'Skyrim Special Edition',
            'Skyrim Anniversary Edition', 
            'Fallout 4',
            'Skyrim Legendary Edition'
        ]
        
        for game in game_priority:
            if detected_games.get(game):
                recommendations['primary_game'] = game
                break
        
        return recommendations
    
    def create_initial_profile(self) -> Dict[str, any]:
        """
        Create an initial user profile based on system detection.
        
        Returns:
            Initial user profile dictionary
        """
        detected_managers = self.detect_mod_managers()
        detected_games = self.detect_games()
        recommendations = self.get_recommended_setup(detected_managers, detected_games)
        
        profile = {
            'system_info': self.system_info,
            'detected_mod_managers': detected_managers,
            'detected_games': detected_games,
            'recommendations': recommendations,
            'experience_level': recommendations['experience_level'],
            'mod_manager': recommendations['mod_manager'],
            'preferred_game': recommendations['primary_game']
        }
        
        log(f"Created initial profile: {recommendations['mod_manager']} user with {recommendations['primary_game']}", 
            debug_only=True, log_type='INFO')
            
        return profile
    
    def load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from persistent storage."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create initial profile if none exists
                return self.create_initial_profile()
        except Exception as e:
            log(f"Failed to load user profile: {e}", log_type='ERROR')
            return self.create_initial_profile()
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        """Save user's preferences to persistent storage."""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing data or create new
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Update with new preferences
            data.update(preferences)
            data['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            log(f"User preferences saved to {self.config_file}", log_type='INFO')
            
        except Exception as e:
            log(f"Failed to save user preferences: {e}", log_type='ERROR')
    
    def mark_tutorial_completed(self, tutorial_type: str = "beginner"):
        """Mark a tutorial as completed."""
        try:
            profile = self.load_user_profile()
            
            if 'tutorials_completed' not in profile:
                profile['tutorials_completed'] = {}
            
            profile['tutorials_completed'][tutorial_type] = {
                'completed': True,
                'completion_date': datetime.now().isoformat(),
                'version': '1.0'  # For future tutorial updates
            }
            
            # Also mark general onboarding as complete
            profile['onboarding_completed'] = True
            profile['onboarding_completion_date'] = datetime.now().isoformat()
            
            self.save_user_preferences(profile)
            log(f"Tutorial '{tutorial_type}' marked as completed", log_type='INFO')
            
        except Exception as e:
            log(f"Failed to mark tutorial completed: {e}", log_type='ERROR')
    
    def is_tutorial_completed(self, tutorial_type: str = "beginner") -> bool:
        """Check if a specific tutorial has been completed."""
        try:
            profile = self.load_user_profile()
            tutorials = profile.get('tutorials_completed', {})
            tutorial_data = tutorials.get(tutorial_type, {})
            return tutorial_data.get('completed', False)
        except Exception as e:
            log(f"Error checking tutorial completion: {e}", log_type='ERROR')
            return False
    
    def is_onboarding_completed(self) -> bool:
        """Check if the user has completed the full onboarding process."""
        try:
            profile = self.load_user_profile()
            return profile.get('onboarding_completed', False)
        except Exception as e:
            log(f"Error checking onboarding completion: {e}", log_type='ERROR')
            return False
    
    def get_tutorial_completion_status(self) -> Dict[str, Any]:
        """Get detailed tutorial completion status."""
        try:
            profile = self.load_user_profile()
            return {
                'onboarding_completed': profile.get('onboarding_completed', False),
                'tutorials_completed': profile.get('tutorials_completed', {}),
                'beginner_tutorial_completed': self.is_tutorial_completed('beginner'),
                'knowledge_checks_completed': profile.get('knowledge_checks_completed', {}),
                'last_updated': profile.get('last_updated')
            }
        except Exception as e:
            log(f"Error getting tutorial status: {e}", log_type='ERROR')
            return {
                'onboarding_completed': False,
                'tutorials_completed': {},
                'beginner_tutorial_completed': False,
                'knowledge_checks_completed': {},
                'last_updated': None
            }
    
    def save_common_paths(self, paths: Dict[str, str]):
        """Save commonly used paths for quick access."""
        try:
            profile = self.load_user_profile()
            
            if 'common_paths' not in profile:
                profile['common_paths'] = {}
            
            profile['common_paths'].update(paths)
            self.save_user_preferences(profile)
            
        except Exception as e:
            log(f"Failed to save common paths: {e}", log_type='ERROR')
    
    def get_common_paths(self) -> Dict[str, str]:
        """Get commonly used paths."""
        try:
            profile = self.load_user_profile()
            return profile.get('common_paths', {})
        except Exception as e:
            log(f"Error getting common paths: {e}", log_type='ERROR')
            return {}
