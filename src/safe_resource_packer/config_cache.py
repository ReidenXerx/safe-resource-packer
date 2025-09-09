"""
Configuration Cache Service

Caches user configuration settings to pre-fill forms on subsequent runs.
Stores the last successful configuration and regenerates it after every successful run.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .dynamic_progress import log


class ConfigCache:
    """Service for caching and managing user configuration settings."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize config cache service.
        
        Args:
            cache_dir: Directory to store cache files (defaults to temp directory)
        """
        if cache_dir is None:
            import tempfile
            cache_dir = os.path.join(tempfile.gettempdir(), "srp_config_cache")
        
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "last_config.json")
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to cache.
        
        Args:
            config: Configuration dictionary to cache
        """
        try:
            # Only save essential configuration fields
            cache_data = {
                'source': config.get('source', ''),
                'generated': config.get('generated', ''),
                'output_pack': config.get('output_pack', ''),
                'output_loose': config.get('output_loose', ''),
                'threads': config.get('threads', 8),
                'debug': config.get('debug', False),
                'game_type': config.get('game_type', 'skyrim'),
                'compression': config.get('compression', 5)
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            log(f"💾 Saved configuration cache", log_type='DEBUG')
            
        except Exception as e:
            log(f"⚠️ Failed to save config cache: {e}", log_type='WARNING')
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Load cached configuration.
        
        Returns:
            Dict with cached configuration or None if not available
        """
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate that essential paths exist
            if not os.path.exists(config.get('source', '')):
                log("📁 Cached source path no longer exists", log_type='DEBUG')
                return None
            
            if not os.path.exists(config.get('generated', '')):
                log("📁 Cached generated path no longer exists", log_type='DEBUG')
                return None
            
            log(f"📁 Loaded configuration cache", log_type='DEBUG')
            return config
            
        except Exception as e:
            log(f"⚠️ Failed to load config cache: {e}", log_type='WARNING')
            return None
    
    def clear_cache(self) -> None:
        """Clear cached configuration."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            log("🧹 Cleared configuration cache", log_type='DEBUG')
        except Exception as e:
            log(f"⚠️ Failed to clear config cache: {e}", log_type='WARNING')
    
    def has_cached_config(self) -> bool:
        """
        Check if cached configuration exists and is valid.
        
        Returns:
            bool: True if valid cached config exists
        """
        config = self.load_config()
        return config is not None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        try:
            cache_file_size = os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
            has_config = self.has_cached_config()
            
            return {
                'has_cached_config': has_config,
                'cache_file_size': cache_file_size,
                'cache_file_path': self.cache_file
            }
        except Exception as e:
            return {
                'has_cached_config': False,
                'cache_file_size': 0,
                'cache_file_path': self.cache_file,
                'error': str(e)
            }


# Global cache instance
_config_cache_instance = None

def get_config_cache() -> ConfigCache:
    """
    Get the global config cache service instance.
    
    Returns:
        ConfigCache: Global config cache service instance
    """
    global _config_cache_instance
    if _config_cache_instance is None:
        _config_cache_instance = ConfigCache()
    return _config_cache_instance
