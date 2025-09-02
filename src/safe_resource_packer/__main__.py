"""
Main entry point for Safe Resource Packer when run as a module.

This allows running the package with: python -m safe_resource_packer
"""

from .console_ui import run_console_ui
from .enhanced_cli import enhanced_main


def main():
    """Main entry point - try console UI first, fall back to enhanced CLI."""
    try:
        # Try to run the console UI
        config = run_console_ui()
        if config:
            # If user provided config through UI, execute it
            from .enhanced_cli import execute_with_config
            return execute_with_config(config)
        else:
            # User cancelled or quit
            return 0
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Error in console UI: {e}")
        print("🔄 Falling back to command-line interface...")
        # Fall back to enhanced CLI
        return enhanced_main()


if __name__ == "__main__":
    exit(main())
