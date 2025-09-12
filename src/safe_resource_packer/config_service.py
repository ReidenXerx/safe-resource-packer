"""
Universal Configuration Service

This service provides centralized configuration management for all Safe Resource Packer functionalities.
It handles config collection, validation, caching, and restoration in a unified way.

Features:
- Universal config collection for all modes (Quick Start, Batch Repacking, Classification)
- Automatic config validation and error handling
- Config caching and restoration
- Support for both Rich UI and basic UI modes
- Consistent config structure across all functionalities
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from .config_cache import get_config_cache


class ConfigService:
    """
    Universal configuration service for Safe Resource Packer.
    
    This service provides a centralized way to collect, validate, cache, and restore
    configuration for all functionalities (Quick Start, Batch Repacking, Classification).
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the configuration service.
        
        Args:
            console: Rich console instance for UI output (optional)
        """
        self.console = console
        self.config_cache = get_config_cache()
    
    def collect_quick_start_config(self, use_cached: bool = True) -> Optional[Dict[str, Any]]:
        """
        Collect configuration for Quick Start mode.
        
        Args:
            use_cached: Whether to offer cached configuration
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        config_type = "quick_start"
        
        # Try to use cached config first
        if use_cached:
            cached_config = self.config_cache.get_cache()
            if cached_config and self._offer_cached_config(cached_config, config_type):
                config = self._build_config_from_cache(cached_config, config_type)
                if config and self._validate_config(config, config_type):
                    return config
        
        # Collect new configuration
        return self._collect_config_interactive(config_type)
    
    def collect_batch_repack_config(self, use_cached: bool = True) -> Optional[Dict[str, Any]]:
        """
        Collect configuration for Batch Repacking mode.
        
        Args:
            use_cached: Whether to offer cached configuration
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        config_type = "batch_repacking"
        
        # Try to use cached config first
        if use_cached:
            cached_config = self.config_cache.get_cache()
            if cached_config and self._offer_cached_config(cached_config, config_type):
                config = self._build_config_from_cache(cached_config, config_type)
                if config and self._validate_config(config, config_type):
                    return config
        
        # Collect new configuration
        return self._collect_config_interactive(config_type)
    
    def collect_classification_config(self, use_cached: bool = True) -> Optional[Dict[str, Any]]:
        """
        Collect configuration for Classification mode.
        
        Args:
            use_cached: Whether to offer cached configuration
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        config_type = "classification_only"
        
        # Try to use cached config first
        if use_cached:
            cached_config = self.config_cache.get_cache()
            if cached_config and self._offer_cached_config(cached_config, config_type):
                config = self._build_config_from_cache(cached_config, config_type)
                if config and self._validate_config(config, config_type):
                    return config
        
        # Collect new configuration
        return self._collect_config_interactive(config_type)
    
    def _offer_cached_config(self, cached_config: Dict[str, Any], config_type: str) -> bool:
        """
        Offer cached configuration to user.
        
        Args:
            cached_config: Cached configuration data
            config_type: Type of configuration (quick_start, batch_repacking, etc.)
            
        Returns:
            True if user wants to use cached config, False otherwise
        """
        if not self.console:
            # Basic UI mode
            print(f"\n⚡ Using Last Configuration:")
            if config_type == "quick_start":
                print(f"📂 Source: {cached_config.get('source', 'N/A')}")
                print(f"📂 Generated: {cached_config.get('generated', 'N/A')}")
                print(f"📦 Pack Output: {cached_config.get('output_pack', 'N/A')}")
                print(f"📁 Loose Output: {cached_config.get('output_loose', 'N/A')}")
            elif config_type == "batch_repacking":
                print(f"📁 Collection: {cached_config.get('collection', 'N/A')}")
                print(f"🎮 Game: {cached_config.get('game_type', 'N/A')}")
            
            return input("Use this configuration? [y/n] (y): ").strip().lower() not in ['n', 'no']
        else:
            # Rich UI mode
            if config_type == "quick_start":
                cache_panel = Panel(
                    "[bold green]⚡ Using Last Configuration[/bold green]\n"
                    f"[dim]📂 Source: {cached_config.get('source', 'N/A')}\n"
                    f"📂 Generated: {cached_config.get('generated', 'N/A')}\n"
                    f"📦 Pack Output: {cached_config.get('output_pack', 'N/A')}\n"
                    f"📁 Loose Output: {cached_config.get('output_loose', 'N/A')}[/dim]",
                    border_style="green",
                    padding=(1, 1)
                )
            elif config_type == "batch_repacking":
                cache_panel = Panel(
                    "[bold green]⚡ Using Last Configuration[/bold green]\n"
                    f"[dim]📁 Collection: {cached_config.get('collection', 'N/A')}\n"
                    f"🎮 Game: {cached_config.get('game_type', 'N/A')}[/dim]",
                    border_style="green",
                    padding=(1, 1)
                )
            else:
                cache_panel = Panel(
                    "[bold green]⚡ Using Last Configuration[/bold green]",
                    border_style="green",
                    padding=(1, 1)
                )
            
            self.console.print(cache_panel)
            self.console.print()
            
            return Confirm.ask("Use this configuration?", default=True)
    
    def _build_config_from_cache(self, cached_config: Dict[str, Any], config_type: str) -> Dict[str, Any]:
        """
        Build configuration from cached data.
        
        Args:
            cached_config: Cached configuration data
            config_type: Type of configuration
            
        Returns:
            Configuration dictionary
        """
        config = {
            'source': cached_config.get('source', ''),
            'generated': cached_config.get('generated', ''),
            'output_pack': cached_config.get('output_pack', './pack'),
            'output_loose': cached_config.get('output_loose', './loose'),
            'output_blacklisted': cached_config.get('output_blacklisted', './blacklisted'),
            'threads': cached_config.get('threads', 8),
            'debug': cached_config.get('debug', False),
            'game_type': cached_config.get('game_type', 'skyrim'),
            'compression': cached_config.get('compression', 5),
            'mode': config_type
        }
        
        # Add mode-specific fields
        if config_type == "batch_repacking":
            config['collection'] = cached_config.get('collection', '')
            config['output_path'] = cached_config.get('output_path', '')
        
        return config
    
    def _validate_config(self, config: Dict[str, Any], config_type: str) -> bool:
        """
        Validate configuration data.
        
        Args:
            config: Configuration to validate
            config_type: Type of configuration
            
        Returns:
            True if valid, False otherwise
        """
        # Validate required directories exist
        if config_type in ["quick_start", "classification_only"]:
            required_dirs = ['source', 'generated']
            for dir_key in required_dirs:
                if not config.get(dir_key) or not os.path.exists(config[dir_key]):
                    if self.console:
                        self.console.print(f"[red]❌ Invalid {dir_key} directory: {config.get(dir_key, 'N/A')}[/red]")
                    else:
                        print(f"❌ Invalid {dir_key} directory: {config.get(dir_key, 'N/A')}")
                    return False
        
        elif config_type == "batch_repacking":
            if not config.get('collection') or not os.path.exists(config['collection']):
                if self.console:
                    self.console.print(f"[red]❌ Invalid collection directory: {config.get('collection', 'N/A')}[/red]")
                else:
                    print(f"❌ Invalid collection directory: {config.get('collection', 'N/A')}")
                return False
        
        # Validate that output directories are different
        if config_type in ["quick_start", "classification_only"]:
            directories = [config['output_pack'], config['output_loose'], config['output_blacklisted']]
            for i, dir1 in enumerate(directories):
                for j, dir2 in enumerate(directories[i+1:], i+1):
                    if os.path.normpath(os.path.abspath(dir1)) == os.path.normpath(os.path.abspath(dir2)):
                        if self.console:
                            self.console.print("[red]❌ Output directories cannot be the same![/red]")
                            self.console.print(f"[red]   Directory {i+1}: {dir1}[/red]")
                            self.console.print(f"[red]   Directory {j+1}: {dir2}[/red]")
                        else:
                            print("❌ Output directories cannot be the same!")
                            print(f"   Directory {i+1}: {dir1}")
                            print(f"   Directory {j+1}: {dir2}")
                        return False
        
        return True
    
    def _collect_config_interactive(self, config_type: str) -> Optional[Dict[str, Any]]:
        """
        Collect configuration interactively from user.
        
        Args:
            config_type: Type of configuration to collect
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        if self.console:
            return self._collect_config_rich(config_type)
        else:
            return self._collect_config_basic(config_type)
    
    def _collect_config_rich(self, config_type: str) -> Optional[Dict[str, Any]]:
        """
        Collect configuration using Rich UI.
        
        Args:
            config_type: Type of configuration to collect
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        # Show header
        if config_type == "quick_start":
            header_text = "🚀 Quick Start Configuration"
            description = "Configure paths and settings for single mod processing"
        elif config_type == "batch_repacking":
            header_text = "📦 Batch Repacking Configuration"
            description = "Configure settings for batch mod processing"
        else:
            header_text = "🔍 Classification Configuration"
            description = "Configure paths for file classification only"
        
        header_panel = Panel(
            f"[bold bright_white]{header_text}[/bold bright_white]\n"
            f"[dim]{description}[/dim]",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()
        
        config = {}
        
        # Collect common fields
        if config_type in ["quick_start", "classification_only"]:
            # Source directory
            source = Prompt.ask(
                "[bold cyan]📂 Source files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="",
                show_default=False
            )
            is_valid, result = self._validate_directory_path(source, "source directory")
            if not is_valid:
                self.console.print(f"[red]❌ {result}[/red]")
                return None
            config['source'] = result
            
            # Generated directory
            generated = Prompt.ask(
                "[bold cyan]🔧 Generated files directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="",
                show_default=False
            )
            is_valid, result = self._validate_directory_path(generated, "generated directory")
            if not is_valid:
                self.console.print(f"[red]❌ {result}[/red]")
                return None
            config['generated'] = result
            
            # Output directories
            config['output_pack'] = Prompt.ask(
                "[bold cyan]📦 Pack files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="./pack",
                show_default=True
            )
            config['output_loose'] = Prompt.ask(
                "[bold cyan]📁 Loose files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="./loose",
                show_default=True
            )
            config['output_blacklisted'] = Prompt.ask(
                "[bold cyan]🚫 Blacklisted files output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="./blacklisted",
                show_default=True
            )
        
        elif config_type == "batch_repacking":
            # Collection directory
            collection = Prompt.ask(
                "[bold cyan]📁 Collection directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="",
                show_default=False
            )
            is_valid, result = self._validate_directory_path(collection, "collection directory")
            if not is_valid:
                self.console.print(f"[red]❌ {result}[/red]")
                return None
            config['collection'] = result
            
            # Output path
            config['output_path'] = Prompt.ask(
                "[bold cyan]📁 Output directory[/bold cyan]\n[dim]💡 Tip: You can drag and drop a folder from Windows Explorer here[/dim]",
                default="./output",
                show_default=True
            )
        
        # Common settings
        config['game_type'] = Prompt.ask(
            "[bold cyan]🎮 Game type[/bold cyan]",
            choices=["skyrim", "fallout4"],
            default="skyrim"
        )
        
        config['compression'] = Prompt.ask(
            "[bold cyan]⚡ Compression level (1-9)[/bold cyan]",
            default="5"
        )
        try:
            config['compression'] = int(config['compression'])
            if config['compression'] < 1 or config['compression'] > 9:
                config['compression'] = 5
        except ValueError:
            config['compression'] = 5
        
        config['threads'] = Prompt.ask(
            "[bold cyan]⚡ Number of threads[/bold cyan]",
            default="8"
        )
        try:
            config['threads'] = int(config['threads'])
        except ValueError:
            config['threads'] = 8
        
        config['debug'] = Confirm.ask(
            "[bold cyan]🐛 Enable debug mode?[/bold cyan]",
            default=False
        )
        
        config['mode'] = config_type
        
        # Validate configuration
        if not self._validate_config(config, config_type):
            return None
        
        # Show summary
        self._show_config_summary(config, config_type)
        
        if Confirm.ask("\nProceed with this configuration?", default=True):
            return config
        else:
            return None
    
    def _collect_config_basic(self, config_type: str) -> Optional[Dict[str, Any]]:
        """
        Collect configuration using basic UI.
        
        Args:
            config_type: Type of configuration to collect
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        config = {}
        
        # Collect common fields
        if config_type in ["quick_start", "classification_only"]:
            config['source'] = input("Source files directory (💡 Tip: You can drag and drop a folder here): ").strip()
            if not config['source'] or not os.path.exists(config['source']):
                print("❌ Invalid source directory!")
                return None
            
            config['generated'] = input("Generated files directory (💡 Tip: You can drag and drop a folder here): ").strip()
            if not config['generated'] or not os.path.exists(config['generated']):
                print("❌ Invalid generated directory!")
                return None
            
            config['output_pack'] = input("Pack files output directory [./pack]: ").strip() or "./pack"
            config['output_loose'] = input("Loose files output directory [./loose]: ").strip() or "./loose"
            config['output_blacklisted'] = input("Blacklisted files output directory [./blacklisted]: ").strip() or "./blacklisted"
        
        elif config_type == "batch_repacking":
            config['collection'] = input("Collection directory (💡 Tip: You can drag and drop a folder here): ").strip()
            if not config['collection'] or not os.path.exists(config['collection']):
                print("❌ Invalid collection directory!")
                return None
            
            config['output_path'] = input("Output directory [./output]: ").strip() or "./output"
        
        # Common settings
        game_type_input = input("Game type (skyrim/fallout4) [skyrim]: ").strip().lower()
        config['game_type'] = game_type_input if game_type_input in ['skyrim', 'fallout4'] else 'skyrim'
        
        compression_input = input("Compression level (1-9) [5]: ").strip()
        try:
            config['compression'] = int(compression_input) if compression_input else 5
            if config['compression'] < 1 or config['compression'] > 9:
                config['compression'] = 5
        except ValueError:
            config['compression'] = 5
        
        threads_input = input("Number of threads [8]: ").strip()
        try:
            config['threads'] = int(threads_input) if threads_input else 8
        except ValueError:
            config['threads'] = 8
        
        debug_input = input("Enable debug mode? [n]: ").strip().lower()
        config['debug'] = debug_input in ['y', 'yes', 'true', '1']
        
        config['mode'] = config_type
        
        # Validate configuration
        if not self._validate_config(config, config_type):
            return None
        
        # Show summary
        self._show_config_summary(config, config_type)
        
        if input("\nProceed with this configuration? [Y/n]: ").strip().lower() not in ['n', 'no']:
            return config
        else:
            return None
    
    def _show_config_summary(self, config: Dict[str, Any], config_type: str) -> None:
        """
        Show configuration summary.
        
        Args:
            config: Configuration to summarize
            config_type: Type of configuration
        """
        if self.console:
            # Rich UI summary
            if config_type == "quick_start":
                summary_text = (
                    f"[bold bright_white]📋 Configuration Summary[/bold bright_white]\n\n"
                    f"[bold green]📂 Source:[/bold green] {config['source']}\n"
                    f"[bold green]📂 Generated:[/bold green] {config['generated']}\n"
                    f"[bold green]📦 Pack Output:[/bold green] {config['output_pack']}\n"
                    f"[bold green]📁 Loose Output:[/bold green] {config['output_loose']}\n"
                    f"[bold green]🚫 Blacklisted Output:[/bold green] {config['output_blacklisted']}\n"
                    f"[bold green]⚡ Threads:[/bold green] {config['threads']}\n"
                    f"[bold green]🐛 Debug:[/bold green] {'Yes' if config['debug'] else 'No'}\n"
                    f"[bold green]🎮 Game:[/bold green] {config['game_type']}\n"
                    f"[bold green]📦 Compression:[/bold green] {config['compression']}"
                )
            elif config_type == "batch_repacking":
                summary_text = (
                    f"[bold bright_white]📋 Configuration Summary[/bold bright_white]\n\n"
                    f"[bold green]📁 Collection:[/bold green] {config['collection']}\n"
                    f"[bold green]📁 Output:[/bold green] {config['output_path']}\n"
                    f"[bold green]🎮 Game:[/bold green] {config['game_type']}\n"
                    f"[bold green]⚡ Threads:[/bold green] {config['threads']}\n"
                    f"[bold green]🐛 Debug:[/bold green] {'Yes' if config['debug'] else 'No'}\n"
                    f"[bold green]📦 Compression:[/bold green] {config['compression']}"
                )
            else:
                summary_text = (
                    f"[bold bright_white]📋 Configuration Summary[/bold bright_white]\n\n"
                    f"[bold green]📂 Source:[/bold green] {config['source']}\n"
                    f"[bold green]📂 Generated:[/bold green] {config['generated']}\n"
                    f"[bold green]📦 Pack Output:[/bold green] {config['output_pack']}\n"
                    f"[bold green]📁 Loose Output:[/bold green] {config['output_loose']}\n"
                    f"[bold green]🚫 Blacklisted Output:[/bold green] {config['output_blacklisted']}\n"
                    f"[bold green]🎮 Game:[/bold green] {config['game_type']}\n"
                    f"[bold green]📦 Compression:[/bold green] {config['compression']}"
                )
            
            summary_panel = Panel(
                summary_text,
                border_style="bright_cyan",
                padding=(1, 2)
            )
            self.console.print(summary_panel)
        else:
            # Basic UI summary
            print(f"\n📋 Configuration Summary:")
            if config_type == "quick_start":
                print(f"📂 Source: {config['source']}")
                print(f"📂 Generated: {config['generated']}")
                print(f"📦 Pack Output: {config['output_pack']}")
                print(f"📁 Loose Output: {config['output_loose']}")
                print(f"🚫 Blacklisted Output: {config['output_blacklisted']}")
                print(f"⚡ Threads: {config['threads']}")
                print(f"🐛 Debug: {'Yes' if config['debug'] else 'No'}")
                print(f"🎮 Game: {config['game_type']}")
                print(f"📦 Compression: {config['compression']}")
            elif config_type == "batch_repacking":
                print(f"📁 Collection: {config['collection']}")
                print(f"📁 Output: {config['output_path']}")
                print(f"🎮 Game: {config['game_type']}")
                print(f"⚡ Threads: {config['threads']}")
                print(f"🐛 Debug: {'Yes' if config['debug'] else 'No'}")
                print(f"📦 Compression: {config['compression']}")
            else:
                print(f"📂 Source: {config['source']}")
                print(f"📂 Generated: {config['generated']}")
                print(f"📦 Pack Output: {config['output_pack']}")
                print(f"📁 Loose Output: {config['output_loose']}")
                print(f"🚫 Blacklisted Output: {config['output_blacklisted']}")
                print(f"🎮 Game: {config['game_type']}")
                print(f"📦 Compression: {config['compression']}")
    
    def _validate_directory_path(self, path: str, path_name: str) -> Tuple[bool, str]:
        """
        Validate a directory path.
        
        Args:
            path: Path to validate
            path_name: Name of the path for error messages
            
        Returns:
            Tuple of (is_valid, result_path)
        """
        if not path:
            return False, f"{path_name} cannot be empty"
        
        if not os.path.exists(path):
            return False, f"{path_name} does not exist: {path}"
        
        if not os.path.isdir(path):
            return False, f"{path_name} is not a directory: {path}"
        
        return True, os.path.abspath(path)
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to cache.
        
        Args:
            config: Configuration to save
        """
        self.config_cache.save_config(config)
    
    def get_cached_config(self) -> Optional[Dict[str, Any]]:
        """
        Get cached configuration.
        
        Returns:
            Cached configuration or None if not available
        """
        return self.config_cache.get_cache()
