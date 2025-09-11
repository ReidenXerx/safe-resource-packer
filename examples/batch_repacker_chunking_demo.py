#!/usr/bin/env python3
"""
Batch Repacker Chunking Demo - Demonstrates CAO-style BSA chunking in batch repacker

This demo shows how the batch repacker now automatically creates chunked BSA archives
when processing large mods, preventing PGPatcher errors.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.batch_repacker import BatchModRepacker
from safe_resource_packer.dynamic_progress import log


def create_large_test_mod(temp_dir: str, mod_name: str, total_size_gb: float = 3.0) -> str:
    """
    Create a large test mod that will trigger chunking.
    
    Args:
        temp_dir: Directory to create test mod in
        mod_name: Name of the mod
        total_size_gb: Total size of assets to create
        
    Returns:
        Path to created mod directory
    """
    mod_dir = os.path.join(temp_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)
    
    # Create ESP file
    esp_path = os.path.join(mod_dir, f"{mod_name}.esp")
    with open(esp_path, 'w') as f:
        f.write("; Test ESP file for chunking demo\n")
    
    # Create large asset files
    game_dirs = ['meshes', 'textures', 'sounds']
    file_extensions = ['.nif', '.dds', '.wav']
    
    bytes_per_gb = 1024 * 1024 * 1024
    target_size = int(total_size_gb * bytes_per_gb)
    current_size = 0
    
    file_counter = 0
    
    for game_dir in game_dirs:
        game_dir_path = os.path.join(mod_dir, game_dir)
        os.makedirs(game_dir_path, exist_ok=True)
        
        while current_size < target_size and file_counter < 50:  # Limit files per directory
            ext = file_extensions[file_counter % len(file_extensions)]
            
            # Create file with random size (between 10MB and 200MB)
            file_size = min(
                max(10 * 1024 * 1024, (file_counter % 20) * 10 * 1024 * 1024),  # 10MB to 200MB
                target_size - current_size  # Don't exceed target
            )
            
            file_path = os.path.join(game_dir_path, f"{mod_name}_asset_{file_counter:04d}{ext}")
            
            # Create file with random content
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size))
            
            current_size += file_size
            file_counter += 1
    
    log(f"✅ Created test mod '{mod_name}' with {current_size / bytes_per_gb:.2f}GB of assets", log_type='SUCCESS')
    return mod_dir


def demonstrate_batch_chunking():
    """Demonstrate the batch repacker chunking functionality."""
    
    log("🚀 Batch Repacker Chunking Demo - CAO-style Archive Creation", log_type='INFO')
    log("=" * 70, log_type='INFO')
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory(prefix="batch_chunking_demo_") as temp_dir:
        log(f"📁 Using temporary directory: {temp_dir}", log_type='INFO')
        
        # Create test mods with large assets
        collection_dir = os.path.join(temp_dir, "mod_collection")
        os.makedirs(collection_dir, exist_ok=True)
        
        # Create a large mod that will trigger chunking
        large_mod_dir = create_large_test_mod(collection_dir, "LargeMod", total_size_gb=3.5)
        
        # Create a smaller mod for comparison
        small_mod_dir = create_large_test_mod(collection_dir, "SmallMod", total_size_gb=0.5)
        
        log(f"\n📦 Testing batch repacker with chunking support...", log_type='INFO')
        
        # Create batch repacker
        repacker = BatchModRepacker.create_with_game_preset("skyrim", threads=4)
        
        # Check BSArch availability
        bsarch_available, bsarch_message = repacker.check_bsarch_availability()
        if not bsarch_available:
            log(f"⚠️ BSArch not available: {bsarch_message}", log_type='WARNING')
            log(f"💡 Install BSArch for proper BSA creation, or the demo will use ZIP fallback", log_type='INFO')
        else:
            log(f"✅ BSArch available: {bsarch_message}", log_type='SUCCESS')
        
        # Discover mods
        discovered_mods = repacker.discover_mods(collection_dir)
        log(f"🔍 Discovered {len(discovered_mods)} mods", log_type='INFO')
        
        # Show discovery summary
        summary = repacker.get_discovery_summary()
        log(f"\n{summary}", log_type='INFO')
        
        # Process mods
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        log(f"\n🚀 Processing mods with automatic chunking...", log_type='INFO')
        
        def progress_callback(current, total, message):
            log(f"📊 Progress: {current}/{total} - {message}", log_type='INFO')
        
        result = repacker.process_mod_collection(
            collection_path=collection_dir,
            output_path=output_dir,
            progress_callback=progress_callback
        )
        
        # Show results
        if result['success']:
            log(f"\n✅ Batch processing completed successfully!", log_type='SUCCESS')
            log(f"📊 Processed: {result['processed']} mods", log_type='SUCCESS')
            log(f"📊 Failed: {result['failed']} mods", log_type='ERROR' if result['failed'] > 0 else 'INFO')
            
            # Show created packages
            log(f"\n📦 Created packages:", log_type='INFO')
            for file in os.listdir(output_dir):
                if file.endswith('.7z'):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    log(f"  • {file} ({file_size / (1024*1024):.1f} MB)", log_type='INFO')
            
            # Show detailed report
            report = repacker.get_summary_report()
            log(f"\n{report}", log_type='INFO')
            
        else:
            log(f"\n❌ Batch processing failed: {result['message']}", log_type='ERROR')
            return False
    
    log(f"\n🎉 Batch Repacker Chunking Demo completed!", log_type='SUCCESS')
    log(f"💡 The batch repacker now automatically creates chunked BSA archives", log_type='INFO')
    log(f"   when processing large mods, preventing PGPatcher errors!", log_type='INFO')
    
    return True


def main():
    """Main demo function."""
    try:
        success = demonstrate_batch_chunking()
        if success:
            log(f"\n✅ Batch Repacker Chunking Demo completed successfully!", log_type='SUCCESS')
            log(f"💡 Your batch repacker now supports CAO-style chunking!", log_type='INFO')
        else:
            log(f"\n❌ Demo failed - check BSArch installation", log_type='ERROR')
            return 1
    except Exception as e:
        log(f"❌ Demo error: {e}", log_type='ERROR')
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
