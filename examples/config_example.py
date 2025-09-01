#!/usr/bin/env python3
"""
Configuration-based example for Safe Resource Packer.

This example shows how to use configuration files or dictionaries
to manage different processing scenarios.
"""

import json
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer import SafeResourcePacker
from safe_resource_packer.utils import log, write_log_file, set_debug


# Example configurations for different scenarios
CONFIGURATIONS = {
    "skyrim_bodyslide": {
        "name": "Skyrim BodySlide Processing",
        "source": "/path/to/skyrim/Data",
        "generated": "/path/to/bodyslide/output",
        "output_pack": "./output/skyrim_pack",
        "output_loose": "./output/skyrim_loose",
        "threads": 8,
        "debug": False,
        "description": "Process BodySlide generated meshes and textures"
    },

    "fallout4_bodyslide": {
        "name": "Fallout 4 BodySlide Processing",
        "source": "/path/to/fallout4/Data",
        "generated": "/path/to/fo4_bodyslide/output",
        "output_pack": "./output/fo4_pack",
        "output_loose": "./output/fo4_loose",
        "threads": 12,
        "debug": False,
        "description": "Process Fallout 4 BodySlide output"
    },

    "generic_resources": {
        "name": "Generic Resource Processing",
        "source": "./source_files",
        "generated": "./generated_files",
        "output_pack": "./output/pack",
        "output_loose": "./output/loose",
        "threads": 4,
        "debug": True,
        "description": "Generic file processing with debug enabled"
    }
}


def load_config_from_file(config_file):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log(f"Config file not found: {config_file}")
        return None
    except json.JSONDecodeError as e:
        log(f"Invalid JSON in config file: {e}")
        return None


def save_config_template(config_file):
    """Save a configuration template file."""
    template = {
        "name": "My Custom Configuration",
        "source": "/path/to/source/files",
        "generated": "/path/to/generated/files",
        "output_pack": "./output/pack",
        "output_loose": "./output/loose",
        "threads": 8,
        "debug": false,
        "description": "Custom processing configuration"
    }

    with open(config_file, 'w') as f:
        json.dump(template, f, indent=2)
    log(f"Configuration template saved to: {config_file}")


def process_with_config(config):
    """Process resources using the provided configuration."""

    log(f"🔧 {config['name']}")
    log("=" * (len(config['name']) + 4))
    log(f"Description: {config['description']}")
    log(f"Source: {config['source']}")
    log(f"Generated: {config['generated']}")
    log(f"Output Pack: {config['output_pack']}")
    log(f"Output Loose: {config['output_loose']}")
    log(f"Threads: {config['threads']}")
    log(f"Debug: {config['debug']}")

    # Set debug mode
    set_debug(config['debug'])

    # Create output directories
    os.makedirs(config['output_pack'], exist_ok=True)
    os.makedirs(config['output_loose'], exist_ok=True)

    # Verify paths exist
    if not os.path.exists(config['source']):
        log(f"❌ Source path does not exist: {config['source']}")
        return False

    if not os.path.exists(config['generated']):
        log(f"❌ Generated path does not exist: {config['generated']}")
        return False

    # Create packer instance
    packer = SafeResourcePacker(
        threads=config['threads'],
        debug=config['debug']
    )

    try:
        # Process the resources
        pack_count, loose_count, skip_count = packer.process_resources(
            source_path=config['source'],
            generated_path=config['generated'],
            output_pack=config['output_pack'],
            output_loose=config['output_loose']
        )

        log(f"\n✅ Processing completed successfully!")
        log(f"📦 Pack files: {pack_count}")
        log(f"📁 Loose files: {loose_count}")
        log(f"⏭️  Skipped files: {skip_count}")

        return True

    except Exception as e:
        log(f"❌ Error during processing: {e}")
        return False


def main():
    """Main function demonstrating configuration usage."""

    if len(sys.argv) < 2:
        log("Usage examples:")
        log("  python config_example.py <config_name>")
        log("  python config_example.py --list")
        log("  python config_example.py --template config.json")
        log("  python config_example.py --file config.json")
        log("")
        log("Available built-in configurations:")
        for name, config in CONFIGURATIONS.items():
            log(f"  {name}: {config['description']}")
        return 1

    arg = sys.argv[1]

    if arg == "--list":
        log("Available configurations:")
        for name, config in CONFIGURATIONS.items():
            log(f"  {name}: {config['description']}")
        return 0

    elif arg == "--template":
        if len(sys.argv) < 3:
            log("Please specify output file: --template config.json")
            return 1
        save_config_template(sys.argv[2])
        return 0

    elif arg == "--file":
        if len(sys.argv) < 3:
            log("Please specify config file: --file config.json")
            return 1
        config = load_config_from_file(sys.argv[2])
        if not config:
            return 1

    elif arg in CONFIGURATIONS:
        config = CONFIGURATIONS[arg]

    else:
        log(f"Unknown configuration: {arg}")
        return 1

    # Process with the selected configuration
    success = process_with_config(config)

    # Write log file
    log_name = config['name'].lower().replace(' ', '_')
    log_file = f"{log_name}_processing.log"
    write_log_file(log_file)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
