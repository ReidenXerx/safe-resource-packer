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
    
    def detect_games(self) -> Dict[str, Optional[str]]:
        """
        Detect installed games and their paths.
        
        Returns:
            Dictionary with game names and their installation paths
        """
        detected_games = {}
        
        if platform.system() == 'Windows':
            detected_games.update(self._detect_windows_games())
        else:
            detected_games.update(self._detect_unix_games())
            
        return detected_games
    
    def _detect_windows_games(self) -> Dict[str, Optional[str]]:
        """Detect games on Windows using Steam, registry, and common paths."""
        games = {
            'Skyrim Special Edition': None,
            'Skyrim Anniversary Edition': None,
            'Fallout 4': None,
            'Skyrim Legendary Edition': None
        }
        
        # Try Steam detection first
        steam_games = self._detect_steam_games()
        games.update(steam_games)
        
        # Try common installation paths
        common_paths = {
            'Skyrim Special Edition': [
                "C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition",
                "C:/Program Files/Steam/steamapps/common/Skyrim Special Edition",
                "C:/Games/Skyrim Special Edition"
            ],
            'Fallout 4': [
                "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4",
                "C:/Program Files/Steam/steamapps/common/Fallout 4",
                "C:/Games/Fallout 4"
            ]
        }
        
        for game, paths in common_paths.items():
            if games[game] is None:  # Only check if not found via Steam
                for path in paths:
                    game_path = Path(path)
                    if game_path.exists() and (game_path / "Data").exists():
                        games[game] = str(game_path)
                        break
        
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
