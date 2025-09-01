#!/usr/bin/env python3
"""
Clean Output Demo - Shows the difference between spammy and clean output
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer import SafeResourcePacker


def create_demo_files():
    """Create demo files for testing clean output."""
    print("🔧 Creating demo files...")
    
    # Create temporary directories
    demo_dir = Path(tempfile.mkdtemp(prefix="clean_output_demo_"))
    
    source_dir = demo_dir / "source"
    generated_dir = demo_dir / "generated"
    
    source_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    
    # Create various types of files to demonstrate different outcomes
    
    # Files that will be identical (skipped)
    identical_files = [
        "meshes/armor/steel/boots.nif",
        "textures/armor/steel/boots.dds",
        "meshes/weapons/sword/iron.nif"
    ]
    
    for file_path in identical_files:
        content = f"Original content for {file_path}"
        
        # Create in source
        source_file = source_dir / file_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(content)
        
        # Create identical in generated
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(content)
    
    # Files that will be different (loose)
    modified_files = [
        "meshes/actors/character/character.nif",
        "textures/actors/character/skin.dds",
        "meshes/armor/custom/modified_armor.nif"
    ]
    
    for file_path in modified_files:
        original_content = f"Original content for {file_path}"
        modified_content = f"MODIFIED content for {file_path}"
        
        # Create in source
        source_file = source_dir / file_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(original_content)
        
        # Create modified in generated
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(modified_content)
    
    # Files that are new (pack)
    new_files = [
        "meshes/armor/custom/new_helmet.nif",
        "textures/armor/custom/new_helmet.dds",
        "meshes/weapons/custom/new_sword.nif",
        "textures/weapons/custom/new_sword.dds",
        "meshes/clutter/custom/new_item.nif",
        "scripts/custom_script.pex",
        "sound/fx/custom_sound.wav"
    ]
    
    for file_path in new_files:
        content = f"New content for {file_path}"
        
        # Only create in generated (not in source)
        gen_file = generated_dir / file_path
        gen_file.parent.mkdir(parents=True, exist_ok=True)
        gen_file.write_text(content)
    
    return demo_dir, source_dir, generated_dir


def demo_clean_vs_spammy():
    """Demonstrate clean vs spammy output."""
    print("🎨 Clean Output Demo")
    print("=" * 50)
    print()
    
    # Create demo files
    demo_dir, source_dir, generated_dir = create_demo_files()
    
    try:
        pack_dir = demo_dir / "pack"
        loose_dir = demo_dir / "loose"
        pack_dir.mkdir()
        loose_dir.mkdir()
        
        print("📊 Demo will show 3 modes:")
        print("1. 🔇 Quiet mode (minimal output)")
        print("2. 🎨 Clean mode (pretty, organized)")  
        print("3. 🗣️  Debug mode (shows the old spammy output)")
        print()
        
        # Mode 1: Quiet mode
        print("1️⃣  QUIET MODE (--quiet)")
        print("-" * 30)
        
        packer_quiet = SafeResourcePacker(threads=4, debug=False)
        start_time = time.time()
        
        # Simulate quiet mode by not showing much
        print("🔄 Processing files quietly...")
        pack_count, loose_count, skip_count = packer_quiet.process_resources(
            str(source_dir), str(generated_dir), str(pack_dir), str(loose_dir)
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Completed: {pack_count} pack, {loose_count} loose, {skip_count} skip ({elapsed:.1f}s)")
        print()
        
        # Clean up for next demo
        import shutil
        shutil.rmtree(pack_dir)
        shutil.rmtree(loose_dir)
        pack_dir.mkdir()
        loose_dir.mkdir()
        
        # Mode 2: Clean mode  
        print("2️⃣  CLEAN MODE (--clean)")
        print("-" * 30)
        
        packer_clean = SafeResourcePacker(threads=4, debug=False)
        
        print("🎨 Processing with clean, colorful output...")
        print("📦 = Pack files (new)")
        print("📁 = Loose files (overrides)")
        print("⏭️ = Skip files (identical)")
        print()
        
        start_time = time.time()
        pack_count, loose_count, skip_count = packer_clean.process_resources(
            str(source_dir), str(generated_dir), str(pack_dir), str(loose_dir)
        )
        elapsed = time.time() - start_time
        
        print()
        print(f"✨ Clean processing completed in {elapsed:.1f}s")
        print(f"📦 Pack: {pack_count} | 📁 Loose: {loose_count} | ⏭️ Skip: {skip_count}")
        print()
        
        # Clean up for next demo
        shutil.rmtree(pack_dir)
        shutil.rmtree(loose_dir)
        pack_dir.mkdir()
        loose_dir.mkdir()
        
        # Mode 3: Debug mode (the old spammy way)
        print("3️⃣  DEBUG MODE (the old spammy way)")
        print("-" * 40)
        print("⚠️  This shows what the output looked like before - very spammy!")
        print()
        
        packer_debug = SafeResourcePacker(threads=4, debug=True)
        start_time = time.time()
        
        pack_count, loose_count, skip_count = packer_debug.process_resources(
            str(source_dir), str(generated_dir), str(pack_dir), str(loose_dir)
        )
        elapsed = time.time() - start_time
        
        print(f"\n📊 Debug processing completed in {elapsed:.1f}s")
        print(f"As you can see, debug mode shows every single file operation - very spammy!")
        print()
        
        # Summary
        print("=" * 60)
        print("🎯 SUMMARY OF IMPROVEMENTS")
        print("=" * 60)
        print("❌ OLD WAY (debug): Shows every file, timestamps, match details")
        print("✅ CLEAN WAY: Clean progress bar, colored icons, summary")
        print("✅ QUIET WAY: Minimal output, just results")
        print()
        print("💡 Usage:")
        print("  safe-resource-packer --quiet     # Minimal output")
        print("  safe-resource-packer --clean     # Clean, pretty output")
        print("  safe-resource-packer --debug     # Full verbose output")
        print()
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(demo_dir)
        print(f"🧹 Cleaned up demo files")


if __name__ == "__main__":
    demo_clean_vs_spammy()
