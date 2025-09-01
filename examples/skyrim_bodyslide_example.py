#!/usr/bin/env python3
"""
Skyrim BodySlide specific example for Safe Resource Packer.

This example shows how to process BodySlide generated files,
which is a common use case for Skyrim modders.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer import SafeResourcePacker
from safe_resource_packer.utils import log, write_log_file, set_debug


def process_bodyslide_output():
    """Process BodySlide output files for safe packing."""

    # Configuration for typical Skyrim BodySlide setup
    config = {
        "source": r"C:\Games\Skyrim Special Edition\Data",  # Your Skyrim Data folder
        "generated": r"C:\Users\YourUser\Documents\My Games\Skyrim Special Edition\CalienteTools\BodySlide\ShapeData",  # BodySlide output
        "output_pack": "./skyrim_pack",  # Files safe to pack into BSA
        "output_loose": "./skyrim_loose",  # Files that should stay loose
        "threads": 12,  # Adjust based on your CPU
        "debug": False  # Set to True for detailed logging
    }

    # Set debug mode
    set_debug(config["debug"])

    # Create output directories
    os.makedirs(config["output_pack"], exist_ok=True)
    os.makedirs(config["output_loose"], exist_ok=True)

    log("🎮 Skyrim BodySlide Resource Processor")
    log("====================================")
    log(f"Source Data: {config['source']}")
    log(f"BodySlide Output: {config['generated']}")
    log(f"Pack Output: {config['output_pack']}")
    log(f"Loose Output: {config['output_loose']}")

    # Verify paths exist
    if not os.path.exists(config["source"]):
        log(f"❌ Source path does not exist: {config['source']}")
        log("Please update the 'source' path in this script to point to your Skyrim Data folder")
        return 1

    if not os.path.exists(config["generated"]):
        log(f"❌ Generated path does not exist: {config['generated']}")
        log("Please update the 'generated' path in this script to point to your BodySlide output")
        return 1

    # Create packer instance
    packer = SafeResourcePacker(
        threads=config["threads"],
        debug=config["debug"]
    )

    try:
        # Process the resources
        pack_count, loose_count, skip_count = packer.process_resources(
            source_path=config["source"],
            generated_path=config["generated"],
            output_pack=config["output_pack"],
            output_loose=config["output_loose"]
        )

        log("\n🎯 BODYSLIDE PROCESSING RESULTS")
        log("===============================")
        log(f"📦 Files ready for BSA packing: {pack_count}")
        log(f"📁 Files to keep loose (overrides): {loose_count}")
        log(f"⏭️  Files skipped (identical): {skip_count}")

        if pack_count > 0:
            log(f"\n✅ You can safely pack the files in '{config['output_pack']}' into a BSA archive")

        if loose_count > 0:
            log(f"⚠️  Keep the files in '{config['output_loose']}' as loose files - they override existing content")

        # Write detailed log
        log_file = "skyrim_bodyslide_processing.log"
        write_log_file(log_file)
        log(f"📋 Detailed log written to: {log_file}")

    except Exception as e:
        log(f"❌ Error during processing: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = process_bodyslide_output()
    sys.exit(exit_code)
