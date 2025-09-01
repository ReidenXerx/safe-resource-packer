#!/usr/bin/env python3
"""
Beautiful Debug Demo - Shows the enhanced colorful debug output
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer import SafeResourcePacker


def create_demo_files_with_variety():
    """Create demo files showcasing different debug scenarios."""
    print("🎨 Creating demo files to showcase beautiful debug output...")

    # Create temporary directories
    demo_dir = Path(tempfile.mkdtemp(prefix="beautiful_debug_demo_"))

    source_dir = demo_dir / "source"
    generated_dir = demo_dir / "generated"

    source_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)

    # Scenario 1: Files that will be identical (SKIP - Yellow ⏭️)
    identical_files = [
        "meshes/armor/steel/boots.nif",
        "textures/armor/steel/boots_d.dds",
        "meshes/weapons/iron/sword.nif"
    ]

    for file_path in identical_files:
        content = f"Identical content for {file_path}"

        # Create in source
        source_file = source_dir / file_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(content)

        # Create identical in generated
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(content)

    # Scenario 2: Files that will be different (OVERRIDE - Magenta 📁)
    modified_files = [
        "meshes/actors/character/femalebody.nif",
        "textures/actors/character/femalebody_1.dds",
        "meshes/armor/custom/modified_cuirass.nif"
    ]

    for file_path in modified_files:
        original_content = f"Original content for {file_path}"
        modified_content = f"MODIFIED BodySlide content for {file_path}"

        # Create in source
        source_file = source_dir / file_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(original_content)

        # Create modified in generated
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(modified_content)

    # Scenario 3: Files that are new (NO MATCH - Blue 📦)
    new_files = [
        "meshes/armor/custom/new_bodyslide_armor.nif",
        "textures/armor/custom/new_bodyslide_armor_d.dds",
        "meshes/armor/custom/new_bodyslide_armor_1.nif",
        "textures/armor/custom/new_bodyslide_armor_n.dds",
        "meshes/weapons/custom/new_weapon.nif",
        "meshes/clutter/custom/new_item.nif",
        "scripts/custom_script.pex"
    ]

    for file_path in new_files:
        content = f"New BodySlide generated content for {file_path}"

        # Only create in generated (not in source)
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(content)

    # Scenario 4: Create a file that will cause an error (for demo purposes)
    error_file = generated_dir / "problematic" / "readonly_file.nif"
    error_file.parent.mkdir(parents=True, exist_ok=True)
    error_file.write_text("This file will cause issues")

    return demo_dir, source_dir, generated_dir


def demo_beautiful_debug():
    """Demonstrate the beautiful debug output."""
    print("🎨 Beautiful Debug Output Demo")
    print("=" * 60)
    print()
    print("This demo shows how debug output now looks with:")
    print("🔍 Green  - MATCH FOUND (files exist in both locations)")
    print("📦 Blue   - NO MATCH (new files, safe to pack)")
    print("⏭️ Yellow - SKIP (identical files)")
    print("📁 Magenta - OVERRIDE (modified files, keep loose)")
    print("❌ Red    - ERRORS (copy failures, hash failures)")
    print("ℹ️ Cyan   - INFO (general information)")
    print("✅ Green  - SUCCESS (operations completed)")
    print()
    print("Watch the beautiful colored output below!")
    print("-" * 60)

    # Create demo files
    demo_dir, source_dir, generated_dir = create_demo_files_with_variety()

    try:
        pack_dir = demo_dir / "pack"
        loose_dir = demo_dir / "loose"
        pack_dir.mkdir()
        loose_dir.mkdir()

        # Create packer with debug mode enabled
        packer = SafeResourcePacker(threads=4, debug=True)

        print("\n🎬 Starting beautiful debug processing...")
        print("=" * 60)

        start_time = time.time()
        pack_count, loose_count, skip_count = packer.process_resources(
            str(source_dir), str(generated_dir), str(pack_dir), str(loose_dir)
        )
        elapsed = time.time() - start_time

        print("=" * 60)
        print("🎯 BEAUTIFUL DEBUG SUMMARY")
        print("=" * 60)
        print(f"✨ Processing completed in {elapsed:.2f}s with beautiful colored output!")
        print(f"📦 Pack files (blue): {pack_count}")
        print(f"📁 Loose files (magenta): {loose_count}")
        print(f"⏭️ Skipped files (yellow): {skip_count}")
        print()
        print("🎨 Color Legend:")
        print("   🔍 Green    = MATCH FOUND (file exists in source)")
        print("   📦 Blue     = NO MATCH (new file, pack it)")
        print("   ⏭️ Yellow   = SKIP (identical file)")
        print("   📁 Magenta  = OVERRIDE (modified file, keep loose)")
        print("   ❌ Red      = ERROR (copy/hash failures)")
        print("   ℹ️ Cyan     = INFO (general information)")
        print("   ✅ Green    = SUCCESS (operation completed)")
        print()
        print("💡 The debug output is now:")
        print("   ✅ Beautifully colored")
        print("   ✅ Easy to scan visually")
        print("   ✅ Clear status indicators")
        print("   ✅ Professional appearance")
        print("   ✅ Still detailed for debugging")
        print()
        print("🚀 Compare this to the old boring monochrome spam!")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(demo_dir)
        print(f"\n🧹 Cleaned up demo files")


def demo_comparison():
    """Show before and after comparison."""
    print("\n" + "=" * 70)
    print("📊 BEFORE vs AFTER COMPARISON")
    print("=" * 70)
    print()
    print("❌ BEFORE (boring, hard to read):")
    print("   [2025-09-01 21:53:57] [MATCH FOUND] file.nif matched to C:\\path\\...")
    print("   [2025-09-01 21:53:57] [SKIP] file2.nif identical")
    print("   [2025-09-01 21:53:57] [NO MATCH] file3.nif → pack")
    print("   [2025-09-01 21:53:57] [OVERRIDE] file4.nif differs")
    print()
    print("✅ AFTER (beautiful, easy to scan):")
    print("   [2025-09-01 21:53:57] 🔍 [MATCH FOUND] file.nif matched to C:\\path\\...")
    print("   [2025-09-01 21:53:57] ⏭️ [SKIP] file2.nif identical")
    print("   [2025-09-01 21:53:57] 📦 [NO MATCH] file3.nif → pack")
    print("   [2025-09-01 21:53:57] 📁 [OVERRIDE] file4.nif differs")
    print()
    print("🎯 Benefits:")
    print("   ✅ Instant visual recognition with colors and icons")
    print("   ✅ Easy to spot errors (red) vs success (green)")
    print("   ✅ Quick scanning for specific operation types")
    print("   ✅ Professional, modern appearance")
    print("   ✅ Still contains all the debug information you need")


if __name__ == "__main__":
    try:
        demo_beautiful_debug()
        demo_comparison()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        print("Note: This demo requires the 'rich' library for colored output")
        print("Install with: pip install rich")
