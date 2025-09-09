#!/usr/bin/env python3
"""
Dynamic Progress Demo - No More Debug Spam! 🚀

This example demonstrates the new dynamic progress system that eliminates
the annoying debug logging spam during classification and other operations.

Instead of thousands of individual log lines flooding your console,
you get a beautiful single-line progress display that updates in real-time!
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.utils import set_debug, log
from safe_resource_packer.dynamic_progress import (
    start_dynamic_progress, update_dynamic_progress, finish_dynamic_progress,
    is_dynamic_progress_enabled, simple_progress_fallback
)

def create_test_files(temp_dir: str, count: int = 100):
    """Create test files for the demo."""
    print(f"📁 Creating {count} test files...")
    
    # Create game-like directory structure
    dirs = [
        "meshes/armor/ebony",
        "textures/armor/ebony", 
        "textures/armor/ebony/female",
        "sounds/fx/magic",
        "scripts/source"
    ]
    
    for dir_path in dirs:
        full_dir = os.path.join(temp_dir, dir_path)
        os.makedirs(full_dir, exist_ok=True)
    
    files_created = []
    for i in range(count):
        if i < count // 3:
            # Texture files
            dir_path = "textures/armor/ebony"
            filename = f"armor_ebony_{i:03d}.dds"
            content = b"DDS FAKE TEXTURE DATA " * 100
        elif i < 2 * count // 3:
            # Mesh files
            dir_path = "meshes/armor/ebony"
            filename = f"armor_ebony_{i:03d}.nif"
            content = b"NIF FAKE MESH DATA " * 50
        else:
            # Script files
            dir_path = "scripts/source"
            filename = f"MyScript{i:03d}.psc"
            content = b"scriptname MyScript extends Quest\n" * 5
        
        file_path = os.path.join(temp_dir, dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        files_created.append(file_path)
    
    print(f"✅ Created {len(files_created)} test files")
    return files_created

def demo_old_spam_logging():
    """Show how the old system created spam."""
    print("\n" + "="*60)
    print("😤 OLD SYSTEM - DEBUG LOGGING SPAM")
    print("="*60)
    print("\nThis is what the old system looked like (simulated):")
    print()
    
    # Simulate the old spam
    files = [
        "armor_ebony_001.dds", "armor_ebony_002.dds", "armor_ebony_003.dds",
        "armor_ebony_001.nif", "armor_ebony_002.nif", "armor_ebony_003.nif",
        "MyScript001.psc", "MyScript002.psc", "MyScript003.psc"
    ]
    
    for i, filename in enumerate(files):
        if i % 3 == 0:
            print(f"[2024-01-15 14:32:{20+i:02d}] [MATCH FOUND] {filename} matched to source/path")
        elif i % 3 == 1:
            print(f"[2024-01-15 14:32:{20+i:02d}] [NO MATCH] {filename} → pack")
        else:
            print(f"[2024-01-15 14:32:{20+i:02d}] [SKIP] {filename} identical")
        
        # Simulate fast spam
        time.sleep(0.1)
    
    print("\n💥 Imagine this but with 10,000+ files!")
    print("😵 Completely unreadable spam that scrolls too fast to follow")
    print("🤯 No way to see overall progress or statistics")
    
    input("\nPress Enter to see the NEW dynamic progress system...")

def demo_new_dynamic_progress(test_files):
    """Show the new beautiful dynamic progress system."""
    print("\n" + "="*60)
    print("🚀 NEW SYSTEM - DYNAMIC PROGRESS (NO SPAM!)")
    print("="*60)
    
    # Enable dynamic progress mode
    set_debug(True, dynamic_progress=True)
    
    if not is_dynamic_progress_enabled():
        print("⚠️  Rich not available, using simple fallback...")
        demo_simple_fallback(test_files)
        return
    
    print("\n✨ Watch the beautiful single-line progress display:")
    print("   • Real-time file processing updates")
    print("   • Live statistics counters")
    print("   • Progress bar with ETA")
    print("   • Current file being processed")
    print("   • NO SPAM! 🎉")
    print()
    
    # Start dynamic progress
    start_dynamic_progress("Demo Classification", len(test_files))
    
    # Simulate file processing
    results = ['skip', 'pack', 'loose', 'skip', 'pack']
    log_types = ['SKIP', 'NO MATCH', 'OVERRIDE', 'MATCH FOUND', 'NO MATCH']
    
    for i, file_path in enumerate(test_files):
        # Simulate processing time
        time.sleep(0.05)  # 50ms per file (much faster than real processing)
        
        # Simulate different results
        result = results[i % len(results)]
        log_type = log_types[i % len(log_types)]
        
        # This would normally be called by the log() function automatically
        update_dynamic_progress(file_path, result, log_type)
        
        # Simulate some errors occasionally
        if i % 50 == 0 and i > 0:
            update_dynamic_progress(file_path, "error", "COPY FAIL")
    
    # Finish and show summary
    finish_dynamic_progress()

def demo_simple_fallback(test_files):
    """Demo the simple fallback when Rich is not available."""
    print("\n📟 Simple Progress Fallback (no Rich):")
    print()
    
    for i, file_path in enumerate(test_files, 1):
        time.sleep(0.02)  # Faster for demo
        filename = os.path.basename(file_path)
        simple_progress_fallback(i, len(test_files), "Classification", filename)
    
    print(f"\n✅ Processing complete! {len(test_files)} files processed")

def demo_log_integration():
    """Show how the new system integrates with existing log() calls."""
    print("\n" + "="*60)
    print("🔧 INTEGRATION WITH EXISTING CODE")
    print("="*60)
    
    print("\nThe beauty is that existing code doesn't need to change!")
    print("The log() function automatically detects classification messages")
    print("and routes them to the dynamic progress display.\n")
    
    # Show code examples
    print("🔍 Example: Existing log calls that now use dynamic progress:")
    print()
    print("  # These calls now automatically update the progress display:")
    print("  log('[MATCH FOUND] file.nif matched to source/file.nif', debug_only=True, log_type='MATCH FOUND')")
    print("  log('[NO MATCH] newfile.dds → pack', debug_only=True, log_type='NO MATCH')")
    print("  log('[SKIP] unchanged.nif identical', debug_only=True, log_type='SKIP')")
    print("  log('[OVERRIDE] modified.dds differs', debug_only=True, log_type='OVERRIDE')")
    print()
    print("  # Non-classification logs still print normally:")
    print("  log('Starting classification process...', log_type='INFO')")
    print()
    
    # Enable debug and show actual integration
    set_debug(True, dynamic_progress=True)
    
    if is_dynamic_progress_enabled():
        print("🎯 Live demonstration (processing a few files):")
        start_dynamic_progress("Integration Demo", 5)
        
        # These log calls will be intercepted and shown in the progress display
        log("[MATCH FOUND] test_file_1.nif matched to source/test_file_1.nif", debug_only=True, log_type='MATCH FOUND')
        time.sleep(0.5)
        
        log("[NO MATCH] new_texture.dds → pack", debug_only=True, log_type='NO MATCH')
        time.sleep(0.5)
        
        log("[SKIP] unchanged_mesh.nif identical", debug_only=True, log_type='SKIP')
        time.sleep(0.5)
        
        log("[OVERRIDE] modified_script.psc differs", debug_only=True, log_type='OVERRIDE')
        time.sleep(0.5)
        
        log("[COPY FAIL] problematic_file.dds: Permission denied", debug_only=True, log_type='COPY FAIL')
        time.sleep(0.5)
        
        finish_dynamic_progress()
    
    print("\n✨ As you can see, no code changes needed!")
    print("   The spam is eliminated automatically! 🎉")

def main():
    """Run the dynamic progress demonstration."""
    print("🎯 Safe Resource Packer - Dynamic Progress Demo")
    print("Eliminating Debug Logging Spam Since 2024! 🚀")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory(prefix="dynamic_progress_demo_") as temp_dir:
        try:
            # Create test files
            test_files = create_test_files(temp_dir, 200)
            
            # Show the problem with the old system
            demo_old_spam_logging()
            
            # Show the new solution
            demo_new_dynamic_progress(test_files)
            
            # Show integration
            demo_log_integration()
            
            print("\n" + "="*60)
            print("🎉 DYNAMIC PROGRESS DEMO COMPLETE!")
            print("="*60)
            print()
            print("🔧 Key Benefits:")
            print("   ✅ No more debug logging spam")
            print("   ✅ Real-time progress visualization")
            print("   ✅ Live statistics and counters")
            print("   ✅ ETA and processing speed")
            print("   ✅ Zero code changes required")
            print("   ✅ Automatic fallback for systems without Rich")
            print()
            print("🚀 Usage:")
            print("   • set_debug(True, dynamic_progress=True)  # Enable dynamic mode")
            print("   • set_debug(True, table_view=True)        # Use legacy table mode")
            print("   • set_debug(True, dynamic_progress=False) # Disable dynamic mode")
            print()
            print("💡 The dynamic progress system is now the default for debug mode!")
            print("   Your classification operations will be much more pleasant to watch! 😎")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
