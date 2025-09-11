"""
Global BSArch Detection Service

Provides a unified BSArch detection system with persistent configuration caching.
Once the user specifies the BSArch location, it's cached and reused across all runs.
"""

import os
import json
import shutil
import platform
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from .config_cache import get_config_cache
from .dynamic_progress import log


class BSArchDetector:
    """Global BSArch detection service with persistent caching."""
    
    def __init__(self):
        """Initialize the BSArch detector."""
        self.config_cache = get_config_cache()
        self._bsarch_cache_file = os.path.join(self.config_cache.cache_dir, "bsarch_config.json")
    
    def _load_bsarch_config(self) -> Optional[Dict[str, Any]]:
        """
        Load cached BSArch configuration.
        
        Returns:
            Dict with cached BSArch config or None if not available
        """
        try:
            if not os.path.exists(self._bsarch_cache_file):
                return None
            
            with open(self._bsarch_cache_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate that the cached path still exists
            bsarch_path = config.get('bsarch_path', '')
            if bsarch_path and os.path.exists(bsarch_path):
                log(f"📁 Loaded cached BSArch path: {bsarch_path}", log_type='DEBUG')
                return config
            else:
                log("📁 Cached BSArch path no longer exists", log_type='DEBUG')
                return None
            
        except Exception as e:
            log(f"⚠️ Failed to load BSArch config cache: {e}", log_type='WARNING')
            return None
    
    def _save_bsarch_config(self, bsarch_path: str, bsarch_dir: str) -> None:
        """
        Save BSArch configuration to cache.
        
        Args:
            bsarch_path: Full path to BSArch executable
            bsarch_dir: Directory containing BSArch
        """
        try:
            config = {
                'bsarch_path': bsarch_path,
                'bsarch_dir': bsarch_dir,
                'platform': platform.system().lower(),
                'timestamp': str(Path().cwd())  # Simple timestamp alternative
            }
            
            with open(self._bsarch_cache_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            log(f"💾 Saved BSArch configuration cache: {bsarch_path}", log_type='DEBUG')
            
        except Exception as e:
            log(f"⚠️ Failed to save BSArch config cache: {e}", log_type='WARNING')
    
    def _find_bsarch_in_path(self) -> Optional[str]:
        """
        Search for BSArch in system PATH.
        
        Returns:
            Path to BSArch executable or None if not found
        """
        # Try both bsarch and BSArch.exe
        for cmd in ['bsarch', 'BSArch.exe']:
            bsarch_path = shutil.which(cmd)
            if bsarch_path:
                log(f"✅ Found BSArch in PATH: {bsarch_path}", log_type='DEBUG')
                return bsarch_path
        
        log("❌ BSArch not found in PATH", log_type='DEBUG')
        return None
    
    def _find_bsarch_in_common_locations(self) -> Optional[str]:
        """
        Search for BSArch in common installation locations.
        
        Returns:
            Path to BSArch executable or None if not found
        """
        system = platform.system().lower()
        
        if system == 'windows':
            common_paths = [
                r"C:\Program Files\BSArch\BSArch.exe",
                r"C:\Program Files (x86)\BSArch\BSArch.exe",
                r"C:\BSArch\BSArch.exe",
                r"C:\Tools\BSArch\BSArch.exe",
                r"C:\Games\BSArch\BSArch.exe"
            ]
        else:
            # Linux/macOS - try Wine locations
            common_paths = [
                os.path.expanduser("~/.wine/drive_c/Program Files/BSArch/BSArch.exe"),
                os.path.expanduser("~/.wine/drive_c/Program Files (x86)/BSArch/BSArch.exe"),
                "/usr/share/BSArch/BSArch.exe",
                "/opt/BSArch/BSArch.exe"
            ]
        
        for path in common_paths:
            if os.path.exists(path):
                log(f"✅ Found BSArch in common location: {path}", log_type='DEBUG')
                return path
        
        log("❌ BSArch not found in common locations", log_type='DEBUG')
        return None
    
    def _ask_user_for_bsarch_location(self) -> Optional[str]:
        """
        Ask user to specify BSArch location.
        
        Returns:
            Path to BSArch executable or None if user cancels
        """
        try:
            # Try to import Rich for better UI
            try:
                from rich.console import Console
                from rich.prompt import Prompt
                from rich.panel import Panel
                console = Console()
                
                # Show helpful information
                info_panel = Panel.fit(
                    "[bold yellow]🔧 BSArch Location Required[/bold yellow]\n"
                    "[dim]BSArch is needed to create BSA/BA2 archives.\n"
                    "Please specify the location of your BSArch installation.[/dim]",
                    border_style="yellow",
                    padding=(1, 2)
                )
                console.print(info_panel)
                console.print()
                
                # Show examples
                examples_panel = Panel(
                    "[bold cyan]📁 Common BSArch Locations:[/bold cyan]\n"
                    "[dim]• C:\\Program Files\\BSArch\\BSArch.exe\n"
                    "• C:\\Games\\BSArch\\BSArch.exe\n"
                    "• C:\\Tools\\BSArch\\BSArch.exe\n"
                    "• ~/.wine/drive_c/Program Files/BSArch/BSArch.exe (Linux/macOS)[/dim]",
                    border_style="cyan",
                    padding=(1, 1)
                )
                console.print(examples_panel)
                console.print()
                
                bsarch_path = Prompt.ask(
                    "[bold green]📁 BSArch executable path[/bold green]\n[dim]💡 Tip: You can drag and drop the BSArch.exe file here[/dim]",
                    default=""
                ).strip()
                
            except ImportError:
                # Fallback to basic input
                print("\n🔧 BSArch Location Required")
                print("BSArch is needed to create BSA/BA2 archives.")
                print("Please specify the location of your BSArch installation.")
                print()
                print("Common locations:")
                print("• C:\\Program Files\\BSArch\\BSArch.exe")
                print("• C:\\Games\\BSArch\\BSArch.exe")
                print("• C:\\Tools\\BSArch\\BSArch.exe")
                print("• ~/.wine/drive_c/Program Files/BSArch/BSArch.exe (Linux/macOS)")
                print()
                bsarch_path = input("BSArch executable path: ").strip()
            
            if not bsarch_path:
                log("❌ User cancelled BSArch location input", log_type='INFO')
                return None
            
            # Validate the path
            if not os.path.exists(bsarch_path):
                log(f"❌ Specified BSArch path does not exist: {bsarch_path}", log_type='ERROR')
                return None
            
            # Check if it's actually BSArch
            if not (bsarch_path.lower().endswith('bsarch.exe') or bsarch_path.lower().endswith('bsarch')):
                log(f"⚠️ Specified path doesn't look like BSArch: {bsarch_path}", log_type='WARNING')
            
            log(f"✅ User specified BSArch path: {bsarch_path}", log_type='INFO')
            return bsarch_path
            
        except Exception as e:
            log(f"❌ Error asking user for BSArch location: {e}", log_type='ERROR')
            return None
    
    def detect_bsarch(self, interactive: bool = True) -> Tuple[bool, str]:
        """
        Detect BSArch executable with persistent caching.
        
        Args:
            interactive: Whether to ask user for location if not found
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # First, try to load from cache
            cached_config = self._load_bsarch_config()
            if cached_config:
                bsarch_path = cached_config['bsarch_path']
                if os.path.exists(bsarch_path):
                    return True, f"BSArch found (cached): {bsarch_path}"
            
            # Try to find in PATH
            bsarch_path = self._find_bsarch_in_path()
            if bsarch_path:
                # Cache this discovery
                bsarch_dir = os.path.dirname(bsarch_path)
                self._save_bsarch_config(bsarch_path, bsarch_dir)
                return True, f"BSArch found in PATH: {bsarch_path}"
            
            # Try common locations
            bsarch_path = self._find_bsarch_in_common_locations()
            if bsarch_path:
                # Cache this discovery
                bsarch_dir = os.path.dirname(bsarch_path)
                self._save_bsarch_config(bsarch_path, bsarch_dir)
                return True, f"BSArch found in common location: {bsarch_path}"
            
            # If not found and interactive, ask user
            if interactive:
                bsarch_path = self._ask_user_for_bsarch_location()
                if bsarch_path:
                    # Cache user's choice
                    bsarch_dir = os.path.dirname(bsarch_path)
                    self._save_bsarch_config(bsarch_path, bsarch_dir)
                    return True, f"BSArch found (user specified): {bsarch_path}"
                else:
                    return False, "BSArch location not specified by user"
            
            # Provide helpful guidance if not found
            system = platform.system().lower()
            if system == 'windows':
                guidance = (
                    "BSArch not found. Try these solutions:\n"
                    "1. Download from: https://www.nexusmods.com/newvegas/mods/64745\n"
                    "2. Extract to C:/Program Files/BSArch/\n"
                    "3. Or add BSArch.exe to your PATH\n"
                    "4. Or specify the path when prompted"
                )
            else:
                guidance = (
                    "BSArch is Windows-only. On Linux/macOS:\n"
                    "1. Use Wine to run BSArch\n"
                    "2. Or the tool will use ZIP fallback (still works)\n"
                    "3. For optimal performance, run on Windows"
                )
            
            return False, guidance
            
        except Exception as e:
            return False, f"Error detecting BSArch: {e}"
    
    def get_bsarch_path(self) -> Optional[str]:
        """
        Get the cached BSArch path if available.
        
        Returns:
            Path to BSArch executable or None if not cached/valid
        """
        cached_config = self._load_bsarch_config()
        if cached_config:
            bsarch_path = cached_config.get('bsarch_path', '')
            if bsarch_path and os.path.exists(bsarch_path):
                return bsarch_path
        return None
    
    def clear_bsarch_cache(self) -> None:
        """Clear cached BSArch configuration."""
        try:
            if os.path.exists(self._bsarch_cache_file):
                os.remove(self._bsarch_cache_file)
            log("🧹 Cleared BSArch configuration cache", log_type='DEBUG')
        except Exception as e:
            log(f"⚠️ Failed to clear BSArch config cache: {e}", log_type='WARNING')


# Global detector instance
_bsarch_detector_instance = None

def get_bsarch_detector() -> BSArchDetector:
    """
    Get the global BSArch detector service instance.
    
    Returns:
        BSArchDetector: Global BSArch detector service instance
    """
    global _bsarch_detector_instance
    if _bsarch_detector_instance is None:
        _bsarch_detector_instance = BSArchDetector()
    return _bsarch_detector_instance


def detect_bsarch_global(interactive: bool = True) -> Tuple[bool, str]:
    """
    Global function to detect BSArch with persistent caching.
    
    Args:
        interactive: Whether to ask user for location if not found
        
    Returns:
        Tuple of (success, message)
    """
    detector = get_bsarch_detector()
    return detector.detect_bsarch(interactive=interactive)


def get_bsarch_path_global() -> Optional[str]:
    """
    Get the cached BSArch path if available.
    
    Returns:
        Path to BSArch executable or None if not cached/valid
    """
    detector = get_bsarch_detector()
    return detector.get_bsarch_path()
