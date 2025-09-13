"""
UI Utilities - Shared utilities for console interface

This module provides shared UI utilities used by both Intelligent Packer and Batch Repacking modes.

Naming Conventions:
- Functions without prefix: Shared utilities used by both modes
"""

import os
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class UIUtilities:
    """Shared UI utilities for console interface."""
    
    def __init__(self, console: Console):
        """
        Initialize UI Utilities.
        
        Args:
            console: Rich console instance for output
        """
        self.console = console
    
    def show_welcome(self):
        """Show welcome message."""
        if not RICH_AVAILABLE:
            self._show_welcome_basic()
            return
        
        welcome_panel = Panel.fit(
            "[bold bright_blue]🎮 Safe Resource Packer[/bold bright_blue]\n"
            "[dim]The Complete Mod Packaging Solution[/dim]\n\n"
            "[bold green]✨ Features:[/bold green]\n"
            "• 🧠 Intelligent file classification\n"
            "• 📦 Complete BSA/BA2 packaging\n"
            "• 🚀 Batch processing capabilities\n"
            "• 🎯 User-friendly interfaces\n"
            "• ⚡ Performance optimized",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def _show_welcome_basic(self):
        """Basic welcome message for when Rich is not available."""
        print("\n" + "=" * 60)
        print("🎮 Safe Resource Packer - The Complete Mod Packaging Solution")
        print("=" * 60)
        print("\n✨ Features:")
        print("• 🧠 Intelligent file classification")
        print("• 📦 Complete BSA/BA2 packaging")
        print("• 🚀 Batch processing capabilities")
        print("• 🎯 User-friendly interfaces")
        print("• ⚡ Performance optimized")
        print()
    
    def show_main_menu(self) -> str:
        """Show main menu and get user selection."""
        if not RICH_AVAILABLE:
            return self._show_main_menu_basic()
        
        menu_panel = Panel(
            "[bold bright_white]🎯 Main Menu[/bold bright_white]\n\n"
            "[bold green]1.[/bold green] 🧠 Intelligent Packer - Smart File Classification & Packaging\n"
            "[bold green]2.[/bold green] 📦 Batch Repacking - Process Multiple Mods\n"
            "[bold green]3.[/bold green] 🔧 Advanced Classification\n"
            "[bold green]4.[/bold green] 🛠️ Tools & System\n"
            "[bold green]5.[/bold green] ❓ Help\n"
            "[bold green]6.[/bold green] 🚪 Exit",
            border_style="bright_white",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        self.console.print()
        
        while True:
            choice = input("Choose an option [1/2/3/4/5/6/q] (1): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', 'q', 'Q', '']:
                return choice if choice else '1'
            print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, 6, or q")
    
    def _show_main_menu_basic(self) -> str:
        """Basic main menu for when Rich is not available."""
        print("\n🎯 Main Menu")
        print("-" * 20)
        print("1. 🧠 Intelligent Packer - Smart File Classification & Packaging")
        print("2. 📦 Batch Repacking - Process Multiple Mods")
        print("3. 🔧 Advanced Classification")
        print("4. 🛠️ Tools & System")
        print("5. ❓ Help")
        print("6. 🚪 Exit")
        print()
        
        while True:
            choice = input("Choose an option [1/2/3/4/5/6/q] (1): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', 'q', 'Q', '']:
                return choice if choice else '1'
            print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, 6, or q")
    
    def validate_directory_path(self, path: str, path_name: str) -> tuple[bool, str]:
        """
        Validate a directory path.
        
        Args:
            path: Path to validate
            path_name: Name of the path for error messages
            
        Returns:
            Tuple of (is_valid, result_path_or_error_message)
        """
        if not path:
            return False, f"{path_name} cannot be empty"
        
        # Handle drag and drop paths (remove quotes if present)
        path = path.strip().strip('"').strip("'")
        
        if not os.path.exists(path):
            return False, f"{path_name} does not exist: {path}"
        
        if not os.path.isdir(path):
            return False, f"{path_name} is not a directory: {path}"
        
        return True, os.path.abspath(path)
    
    def show_processing_header(self, config: Dict[str, Any]):
        """Show processing header with configuration."""
        if not RICH_AVAILABLE:
            self._show_processing_header_basic(config)
            return
        
        header_panel = Panel(
            "[bold bright_white]🚀 Starting Processing[/bold bright_white]\n\n"
            f"[bold green]📁 Source:[/bold green] {config.get('source', 'N/A')}\n"
            f"[bold green]🔧 Generated:[/bold green] {config.get('generated', 'N/A')}\n"
            f"[bold green]📦 Pack Output:[/bold green] {config.get('output_pack', 'N/A')}\n"
            f"[bold green]📁 Loose Output:[/bold green] {config.get('output_loose', 'N/A')}\n"
            f"[bold green]⚡ Threads:[/bold green] {config.get('threads', 8)}\n"
            f"[bold green]🐛 Debug:[/bold green] {'Yes' if config.get('debug', False) else 'No'}",
            border_style="bright_white",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def _show_processing_header_basic(self, config: Dict[str, Any]):
        """Basic processing header for when Rich is not available."""
        print("\n🚀 Starting Processing")
        print("-" * 30)
        print(f"📁 Source: {config.get('source', 'N/A')}")
        print(f"🔧 Generated: {config.get('generated', 'N/A')}")
        print(f"📦 Pack Output: {config.get('output_pack', 'N/A')}")
        print(f"📁 Loose Output: {config.get('output_loose', 'N/A')}")
        print(f"⚡ Threads: {config.get('threads', 8)}")
        print(f"🐛 Debug: {'Yes' if config.get('debug', False) else 'No'}")
        print()
    
    def show_success_message(self, message: str):
        """Show success message."""
        if not RICH_AVAILABLE:
            print(f"✅ {message}")
            return
        
        success_panel = Panel(
            f"[bold green]✅ {message}[/bold green]",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(success_panel)
    
    def show_error_message(self, message: str):
        """Show error message."""
        if not RICH_AVAILABLE:
            print(f"❌ {message}")
            return
        
        error_panel = Panel(
            f"[bold red]❌ {message}[/bold red]",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(error_panel)
    
    def show_warning_message(self, message: str):
        """Show warning message."""
        if not RICH_AVAILABLE:
            print(f"⚠️ {message}")
            return
        
        warning_panel = Panel(
            f"[bold yellow]⚠️ {message}[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(warning_panel)
