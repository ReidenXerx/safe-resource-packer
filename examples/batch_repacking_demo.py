#!/usr/bin/env python3
"""
Batch Mod Repacking Demo

This example demonstrates the new batch repacking functionality that can automatically
process collections of mods, each with their own ESP/ESL/ESM files and loose assets.

Expected folder structure:
ModCollection/
├── ModA/
│   ├── ModA.esp
│   ├── meshes/
│   │   └── actors/character/facegendata/...
│   ├── textures/
│   │   └── actors/character/female/...
│   └── scripts/
├── ModB/
│   ├── ModB.esm
│   ├── meshes/
│   └── textures/
└── ModC/
    ├── ModC.esl
    └── sounds/

This will produce:
Output/
├── ModA_v1.0.7z (contains ModA.esp + ModA_Assets.bsa)
├── ModB_v1.0.7z (contains ModB.esm + ModB_Assets.ba2)  
└── ModC_v1.0.7z (contains ModC.esl + ModC_Assets.bsa)
"""

import os
import sys
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.batch_repacker import BatchModRepacker


def create_demo_mod_collection():
    """Create a demo mod collection for testing."""
    
    # Create temporary directory for demo
    demo_dir = tempfile.mkdtemp(prefix="batch_demo_")
    print(f"📁 Created demo collection at: {demo_dir}")
    
    # Create three example mods
    mods_data = [
        {
            'name': 'BeautifulNPCs',
            'plugin': 'BeautifulNPCs.esp',
            'assets': {
                'meshes/actors/character/facegendata/facetint/BeautifulNPCs.esp/': ['00000001.dds', '00000002.dds'],
                'textures/actors/character/female/': ['body_1.dds', 'hands_1.dds', 'face_1.dds'],
                'meshes/actors/character/character assets/': ['body_1.nif', 'hands_1.nif']
            }
        },
        {
            'name': 'WeaponPack',
            'plugin': 'WeaponPack.esm',
            'assets': {
                'meshes/weapons/sword/': ['mysword.nif', 'mysword_1st.nif'],
                'textures/weapons/sword/': ['mysword.dds', 'mysword_n.dds'],
                'meshes/armor/shield/': ['myshield.nif'],
                'textures/armor/shield/': ['myshield.dds']
            }
        },
        {
            'name': 'SoundEnhancement',
            'plugin': 'SoundEnhancement.esl',
            'assets': {
                'sound/fx/': ['newambient.wav', 'newmusic.wav'],
                'scripts/': ['SoundScript.pex']
            }
        }
    ]
    
    for mod_data in mods_data:
        mod_dir = os.path.join(demo_dir, mod_data['name'])
        os.makedirs(mod_dir, exist_ok=True)
        
        # Create plugin file
        plugin_path = os.path.join(mod_dir, mod_data['plugin'])
        with open(plugin_path, 'wb') as f:
            # Create a minimal ESP header (just for demo)
            f.write(b'TES4' + b'\\x00' * 100)  # Minimal ESP structure
        
        # Create asset files
        for asset_dir, files in mod_data['assets'].items():
            full_asset_dir = os.path.join(mod_dir, asset_dir)
            os.makedirs(full_asset_dir, exist_ok=True)
            
            for filename in files:
                asset_path = os.path.join(full_asset_dir, filename)
                with open(asset_path, 'wb') as f:
                    # Create dummy file content based on extension
                    if filename.endswith('.dds'):
                        f.write(b'DDS ' + b'\\x00' * 1000)  # Dummy texture
                    elif filename.endswith('.nif'):
                        f.write(b'Gamebryo File Format' + b'\\x00' * 500)  # Dummy mesh
                    elif filename.endswith('.wav'):
                        f.write(b'RIFF' + b'\\x00' * 2000)  # Dummy audio
                    else:
                        f.write(b'Demo file content for ' + filename.encode())
    
    print(f"✅ Created {len(mods_data)} demo mods")
    return demo_dir


def demo_batch_discovery():
    """Demonstrate batch mod discovery."""
    
    print("\\n" + "="*60)
    print("🔍 BATCH MOD DISCOVERY DEMO")
    print("="*60)
    
    # Create demo collection
    collection_path = create_demo_mod_collection()
    
    try:
        # Initialize batch repacker
        batch_repacker = BatchModRepacker(game_type='skyrim')
        
        # Discover mods
        print("\\n📋 Discovering mods...")
        discovered_mods = batch_repacker.discover_mods(collection_path)
        
        if discovered_mods:
            print(f"\\n✅ Found {len(discovered_mods)} mods:")
            
            for i, mod in enumerate(discovered_mods, 1):
                print(f"\\n{i}. {mod.mod_name}")
                print(f"   Plugin: {mod.esp_file} ({mod.esp_type})")
                print(f"   Assets: {len(mod.asset_files)} files")
                print(f"   Size: {mod.asset_size:,} bytes")
                print(f"   Categories: {', '.join(mod.asset_categories)}")
        else:
            print("❌ No mods discovered!")
        
        return collection_path, discovered_mods
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return collection_path, []


def demo_batch_processing():
    """Demonstrate full batch processing."""
    
    print("\\n" + "="*60)
    print("📦 BATCH PROCESSING DEMO")
    print("="*60)
    
    # Get discovered mods
    collection_path, discovered_mods = demo_batch_discovery()
    
    if not discovered_mods:
        print("⚠️ No mods to process")
        return
    
    # Create output directory
    output_path = tempfile.mkdtemp(prefix="batch_output_")
    print(f"\\n📤 Output directory: {output_path}")
    
    try:
        # Initialize batch repacker
        batch_repacker = BatchModRepacker(game_type='skyrim', threads=2)
        batch_repacker.discovered_mods = discovered_mods
        
        # Progress callback
        def progress_callback(current, total, message):
            print(f"📦 [{current+1}/{total}] {message}")
        
        # Process collection
        print("\\n🚀 Starting batch processing...")
        results = batch_repacker.process_mod_collection(
            collection_path=collection_path,
            output_path=output_path,
            progress_callback=progress_callback
        )
        
        # Show results
        print("\\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        
        if results['success']:
            print(f"✅ Batch processing completed!")
            print(f"✅ Processed: {results['processed']} mods")
            print(f"❌ Failed: {results['failed']} mods")
            
            # List output files
            print("\\n📦 Generated packages:")
            for file in os.listdir(output_path):
                if file.endswith('.7z'):
                    file_path = os.path.join(output_path, file)
                    size = os.path.getsize(file_path)
                    print(f"  • {file} ({size:,} bytes)")
            
            # Show summary
            print("\\n" + batch_repacker.get_summary_report())
            
        else:
            print(f"❌ Batch processing failed: {results['message']}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\\n🧹 Cleaning up demo files...")
        shutil.rmtree(collection_path, ignore_errors=True)
        shutil.rmtree(output_path, ignore_errors=True)
        print("✅ Cleanup complete")


if __name__ == "__main__":
    print("🎯 Safe Resource Packer - Batch Repacking Demo")
    print("This demo shows how to automatically repack collections of mods.")
    print()
    
    try:
        demo_batch_processing()
        
    except KeyboardInterrupt:
        print("\\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n👋 Demo complete!")
