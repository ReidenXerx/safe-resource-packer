#!/usr/bin/env python3
"""
Console UI Demo

Demonstrates the interactive console user interface that makes the tool
accessible to non-technical users. No command-line knowledge required!
"""

import os
import sys

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    """Demonstrate the console UI."""

    print("🎮 Safe Resource Packer - Console UI Demo")
    print("=" * 50)
    print()
    print("This demo shows the interactive console interface that makes")
    print("Safe Resource Packer accessible to everyone - no technical")
    print("knowledge or command-line experience required!")
    print()
    print("Key Features:")
    print("✅ Beautiful interactive menus")
    print("✅ Step-by-step wizards")
    print("✅ Path validation and help")
    print("✅ System setup checking")
    print("✅ Automatic tool installation")
    print("✅ Built-in help and examples")
    print()

    try:
        from safe_resource_packer.console_ui import run_console_ui

        print("🚀 Launching Console UI...")
        print("(This will show the full interactive interface)")
        print()

        # Run the console UI
        config = run_console_ui()

        if config:
            print("\n" + "=" * 50)
            print("📋 CONFIGURATION GENERATED")
            print("=" * 50)
            print("The console UI would now execute with these settings:")
            print()

            for key, value in config.items():
                print(f"  {key}: {value}")

            print()
            print("🎯 This configuration would be passed to the CLI system")
            print("   to execute the actual processing - no manual command")
            print("   construction required!")
        else:
            print("\n👋 User cancelled or exited the interface.")

    except ImportError as e:
        print(f"❌ Could not import console UI: {e}")
        print("Make sure the package is installed: pip install -e .")
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user.")
    except Exception as e:
        print(f"❌ Error running demo: {e}")


if __name__ == "__main__":
    main()
