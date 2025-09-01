#!/usr/bin/env python3
"""
Basic usage example for Safe Resource Packer.

This example demonstrates how to use the SafeResourcePacker class
programmatically in your own Python scripts.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer import SafeResourcePacker
from safe_resource_packer.utils import log, write_log_file, set_debug


def main():
    """Example of basic usage."""

    # Enable debug mode for detailed output
    set_debug(True)

    # Example paths - adjust these for your actual use case
    source_path = "/path/to/your/skyrim/Data"
    generated_path = "/path/to/your/bodyslide/output"
    output_pack = "./output/pack"
    output_loose = "./output/loose"

    # Create output directories
    os.makedirs(output_pack, exist_ok=True)
    os.makedirs(output_loose, exist_ok=True)

    # Create packer instance
    packer = SafeResourcePacker(threads=8, debug=True)

    try:
        log("Starting resource processing...")

        # Process the resources
        pack_count, loose_count, skip_count = packer.process_resources(
            source_path=source_path,
            generated_path=generated_path,
            output_pack=output_pack,
            output_loose=output_loose
        )

        # Print results
        log(f"Files classified for packing: {pack_count}")
        log(f"Files classified as loose overrides: {loose_count}")
        log(f"Files skipped (identical): {skip_count}")

        # Write log file
        write_log_file("example_run.log")

    except Exception as e:
        log(f"Error during processing: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
