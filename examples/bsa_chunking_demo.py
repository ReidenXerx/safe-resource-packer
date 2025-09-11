#!/usr/bin/env python3
"""
BSA Chunking Demo - Demonstrates CAO-style BSA chunking functionality

This demo shows how Safe Resource Packer now creates chunked BSA archives
similar to Cathedral Assets Optimizer (CAO), with a 2GB limit per chunk
to prevent PGPatcher and other tools from encountering errors.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.bsarch_service import execute_bsarch_chunked_universal
from safe_resource_packer.dynamic_progress import log


def create_test_files(temp_dir: str, total_size_gb: float = 3.0) -> list[str]:
    """
    Create test files that exceed the 2GB chunk limit.
    
    Args:
        temp_dir: Directory to create test files in
        total_size_gb: Total size of test files to create
        
    Returns:
        List of created file paths
    """
    log(f"📁 Creating test files totaling {total_size_gb}GB...", log_type='INFO')
    
    # Create different types of game files
    game_dirs = ['meshes', 'textures', 'sounds', 'scripts']
    file_extensions = ['.nif', '.dds', '.wav', '.pex']
    
    files_created = []
    bytes_per_gb = 1024 * 1024 * 1024
    target_size = int(total_size_gb * bytes_per_gb)
    current_size = 0
    
    file_counter = 0
    
    while current_size < target_size:
        # Choose random directory and extension
        game_dir = game_dirs[file_counter % len(game_dirs)]
        ext = file_extensions[file_counter % len(file_extensions)]
        
        # Create directory structure
        file_dir = os.path.join(temp_dir, game_dir, f"subdir_{file_counter // 10}")
        os.makedirs(file_dir, exist_ok=True)
        
        # Create file with random size (between 1MB and 100MB)
        file_size = min(
            max(1024 * 1024, (file_counter % 100) * 1024 * 1024),  # 1MB to 100MB
            target_size - current_size  # Don't exceed target
        )
        
        file_path = os.path.join(file_dir, f"test_file_{file_counter:04d}{ext}")
        
        # Create file with random content
        with open(file_path, 'wb') as f:
            f.write(os.urandom(file_size))
        
        files_created.append(file_path)
        current_size += file_size
        file_counter += 1
        
        if file_counter % 10 == 0:
            log(f"  📄 Created {file_counter} files ({current_size / bytes_per_gb:.2f}GB)", log_type='DEBUG')
    
    log(f"✅ Created {len(files_created)} test files ({current_size / bytes_per_gb:.2f}GB total)", log_type='SUCCESS')
    return files_created


def demonstrate_chunking():
    """Demonstrate the BSA chunking functionality."""
    
    log("🚀 BSA Chunking Demo - CAO-style Archive Creation", log_type='INFO')
    log("=" * 60, log_type='INFO')
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory(prefix="bsa_chunking_demo_") as temp_dir:
        log(f"📁 Using temporary directory: {temp_dir}", log_type='INFO')
        
        # Create test files that exceed 2GB
        test_files = create_test_files(temp_dir, total_size_gb=3.5)
        
        # Set up output path
        output_base_path = os.path.join(temp_dir, "test_mod")
        
        log(f"\n📦 Creating chunked BSA archives...", log_type='INFO')
        log(f"📊 Input: {len(test_files)} files", log_type='INFO')
        log(f"📊 Target: 2GB chunks (CAO-style)", log_type='INFO')
        
        # Create chunked archives
        success, message, created_archives = execute_bsarch_chunked_universal(
            source_dir=temp_dir,
            output_base_path=output_base_path,
            files=test_files,
            game_type="skyrim",
            max_chunk_size_gb=2.0,
            interactive=False
        )
        
        if success:
            log(f"\n✅ Chunking successful!", log_type='SUCCESS')
            log(f"📝 Message: {message}", log_type='INFO')
            log(f"📦 Created {len(created_archives)} archives:", log_type='INFO')
            
            total_size = 0
            for i, archive_path in enumerate(created_archives):
                if os.path.exists(archive_path):
                    size = os.path.getsize(archive_path)
                    total_size += size
                    size_mb = size / (1024 * 1024)
                    log(f"  {i+1}. {os.path.basename(archive_path)} ({size_mb:.1f} MB)", log_type='INFO')
                else:
                    log(f"  {i+1}. {os.path.basename(archive_path)} (NOT FOUND)", log_type='ERROR')
            
            log(f"\n📊 Total archive size: {total_size / (1024*1024):.1f} MB", log_type='INFO')
            log(f"📊 Average chunk size: {total_size / len(created_archives) / (1024*1024):.1f} MB", log_type='INFO')
            
            # Verify chunk naming follows CAO pattern
            chunk_names = [os.path.basename(arch) for arch in created_archives]
            log(f"\n🏷️ Chunk naming pattern:", log_type='INFO')
            for name in chunk_names:
                log(f"  • {name}", log_type='INFO')
            
            # Check if naming follows CAO pattern (pack.bsa, pack0.bsa, pack1.bsa, etc.)
            has_pack_naming = any('pack' in name.lower() for name in chunk_names)
            if has_pack_naming:
                log(f"✅ CAO-style naming detected!", log_type='SUCCESS')
            else:
                log(f"⚠️ Naming pattern may not match CAO exactly", log_type='WARNING')
                
        else:
            log(f"\n❌ Chunking failed: {message}", log_type='ERROR')
            return False
    
    log(f"\n🎉 Demo completed successfully!", log_type='SUCCESS')
    log(f"💡 This demonstrates how Safe Resource Packer now creates", log_type='INFO')
    log(f"   chunked BSA archives like CAO to prevent PGPatcher errors!", log_type='INFO')
    
    return True


def main():
    """Main demo function."""
    try:
        success = demonstrate_chunking()
        if success:
            log(f"\n✅ BSA Chunking Demo completed successfully!", log_type='SUCCESS')
            log(f"💡 Your Safe Resource Packer now supports CAO-style chunking!", log_type='INFO')
        else:
            log(f"\n❌ Demo failed - check BSArch installation", log_type='ERROR')
            return 1
    except Exception as e:
        log(f"❌ Demo error: {e}", log_type='ERROR')
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
