#!/usr/bin/env python3
"""
Compression Improvements Demo - Safe Resource Packer

This example demonstrates the new compression improvements:
1. Better 7z tool detection (avoiding crappy Windows defaults)
2. Compression tool logging (shows which tool is being used)
3. Progress tracking with percentage updates
4. Updated next steps (no manual BSA/BA2 creation needed)

Run this to see the enhanced compression system in action!
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.packaging.compressor import Compressor
from safe_resource_packer.utils import log, set_debug

def create_test_files(temp_dir: str, file_count: int = 50):
    """Create test files for compression demo."""
    print(f"📁 Creating {file_count} test files...")
    
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
    
    # Create test files with different sizes
    files_created = []
    
    for i in range(file_count):
        if i < 20:
            # Texture files (larger)
            dir_path = "textures/armor/ebony"
            filename = f"armor_ebony_{i:03d}.dds"
            content = b"DDS FAKE TEXTURE DATA " * 1000  # ~20KB
        elif i < 35:
            # Mesh files (medium)
            dir_path = "meshes/armor/ebony"
            filename = f"armor_ebony_{i:03d}.nif"
            content = b"NIF FAKE MESH DATA " * 500  # ~10KB
        elif i < 45:
            # Sound files (larger)
            dir_path = "sounds/fx/magic"
            filename = f"spell_effect_{i:03d}.wav"
            content = b"WAV FAKE AUDIO DATA " * 2000  # ~40KB
        else:
            # Script files (small)
            dir_path = "scripts/source"
            filename = f"MyScript{i:03d}.psc"
            content = b"scriptname MyScript extends Quest\n" * 10  # ~300B
        
        file_path = os.path.join(temp_dir, dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        files_created.append(file_path)
    
    print(f"✅ Created {len(files_created)} test files")
    return files_created

def demo_compression_tools():
    """Demonstrate the improved compression tool detection and logging."""
    print("\n" + "="*60)
    print("🔧 COMPRESSION TOOL DETECTION DEMO")
    print("="*60)
    
    # Enable debug mode to see detailed logging
    set_debug(True)
    
    # Create compressor instance
    compressor = Compressor(compression_level=5)
    
    # This will trigger tool detection and logging
    print("\n🔍 Detecting available compression tools...")
    compressor._log_compression_tool_selection()
    
    return compressor

def demo_compression_with_progress(compressor: Compressor, test_files: list, temp_dir: str):
    """Demonstrate compression with progress tracking."""
    print("\n" + "="*60)
    print("📦 COMPRESSION WITH PROGRESS TRACKING DEMO")
    print("="*60)
    
    archive_path = os.path.join(temp_dir, "demo_archive.7z")
    
    print(f"\n🚀 Starting compression of {len(test_files)} files...")
    print("   Watch for:")
    print("   • Tool selection logging")
    print("   • Progress percentage updates")  
    print("   • Performance optimizations")
    
    success, message = compressor.compress_files(test_files, archive_path)
    
    if success:
        print(f"\n✅ Compression completed successfully!")
        print(f"📁 Archive created: {archive_path}")
        
        # Show archive info
        if os.path.exists(archive_path):
            size_mb = os.path.getsize(archive_path) / (1024 * 1024)
            print(f"📊 Archive size: {size_mb:.2f} MB")
            
            # Calculate compression ratio
            total_size = sum(os.path.getsize(f) for f in test_files if os.path.exists(f))
            total_mb = total_size / (1024 * 1024)
            ratio = (1 - size_mb / total_mb) * 100 if total_mb > 0 else 0
            print(f"📈 Original size: {total_mb:.2f} MB")
            print(f"🎯 Compression ratio: {ratio:.1f}%")
    else:
        print(f"❌ Compression failed: {message}")
    
    return success

def demo_next_steps_improvements():
    """Demonstrate the improved next steps messaging."""
    print("\n" + "="*60)
    print("📋 IMPROVED NEXT STEPS DEMO")
    print("="*60)
    
    print("\n🔄 OLD vs NEW Next Steps:")
    
    print("\n❌ OLD (Manual BSA/BA2 creation):")
    print("   1. Pack the files in the pack directory into BSA/BA2")
    print("   2. Use tools like BSArch, Cathedral Assets Optimizer...")
    print("   3. Keep loose files as-is in your mod manager")
    
    print("\n✅ NEW (Automatic BSA/BA2 creation):")
    print("   1. 📦 Install packed files (BSA/BA2 + ESP)")
    print("      BSA/BA2 archives are automatically created for optimal game performance")
    print("   2. 📁 Install loose files to your mod manager")
    print("      These files override packed content and should stay loose")
    print("   3. 🎮 Test your mod setup in-game")
    print("   4. 📋 Check the log file for any errors or warnings")
    print("   💡 Performance Tip:")
    print("      BSA/BA2 archives load faster than loose files")
    print("      Only loose files override packed content when needed")

def main():
    """Run the compression improvements demonstration."""
    print("🎯 Safe Resource Packer - Compression Improvements Demo")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory(prefix="compression_demo_") as temp_dir:
        try:
            # Step 1: Create test files
            test_files = create_test_files(temp_dir, file_count=100)
            
            # Step 2: Demo tool detection
            compressor = demo_compression_tools()
            
            # Step 3: Demo compression with progress
            success = demo_compression_with_progress(compressor, test_files, temp_dir)
            
            # Step 4: Demo improved next steps
            demo_next_steps_improvements()
            
            print("\n" + "="*60)
            print("🎉 DEMO COMPLETED!")
            print("="*60)
            
            if success:
                print("✅ All compression improvements working correctly!")
                print("\n🔧 Key Improvements:")
                print("   • Better 7z tool detection (avoids Windows defaults)")
                print("   • Compression tool logging (shows which tool is used)")
                print("   • Progress tracking with percentages")
                print("   • Updated next steps (no manual BSA/BA2 creation)")
                print("   • Performance optimizations for large file sets")
            else:
                print("⚠️  Some compression methods may not be available")
                print("   Install py7zr or 7-Zip for best results")
            
            print(f"\n📁 Demo files were in: {temp_dir}")
            print("   (Automatically cleaned up)")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
