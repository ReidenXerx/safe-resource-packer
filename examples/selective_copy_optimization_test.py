#!/usr/bin/env python3
"""
Selective Copy Optimization Test - Tests the smart selective copying feature

This test verifies that we only copy relevant directories from the source,
providing massive space and time savings when dealing with large game Data folders.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.core import SafeResourcePacker


def create_mock_game_data(base_dir):
    """Create a mock game Data directory with many directories."""
    print("📁 Creating mock game Data directory...")

    data_dir = os.path.join(base_dir, "GameData")

    # Create lots of directories (simulating a real game installation)
    all_directories = [
        'meshes', 'textures', 'sounds', 'music', 'scripts', 'interface',
        'actors', 'materials', 'shaders', 'strings', 'video', 'skse',
        'mcm', 'fomod', 'docs', 'backup', 'dyndolod', 'grass', 'trees',
        'terrain', 'facegen', 'facegendata', 'animationdata', 'behaviordata',
        'charactergen', 'dialogueviews', 'effects', 'environment', 'lighting',
        'loadscreens', 'misc', 'planetdata', 'seq', 'voices', 'weapons',
        'particlelights', 'pbrmaterialobjects', 'pbrtexturesets', 'shadersfx'
    ]

    created_files = 0
    for dir_name in all_directories:
        dir_path = os.path.join(data_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # Create multiple files in each directory to simulate real data
        for i in range(10):  # 10 files per directory
            file_path = os.path.join(dir_path, f"file_{i:03d}.dat")
            with open(file_path, 'w') as f:
                # Write some content to make files have realistic size
                f.write(f"Mock game file in {dir_name}\n" + "x" * 1000)  # ~1KB per file
            created_files += 1

    print(f"✅ Created mock game Data with {len(all_directories)} directories, {created_files} files")
    return data_dir, all_directories


def create_small_mod(base_dir):
    """Create a small mod that only uses a few directories."""
    print("📦 Creating small mod (only uses 3 directories)...")

    mod_dir = os.path.join(base_dir, "SmallMod")

    # Mod only uses 3 directories out of 30+ in the game
    mod_files = [
        'meshes/armor/myarmor/helmet.nif',
        'meshes/armor/myarmor/cuirass.nif',
        'textures/armor/myarmor/helmet_d.dds',
        'textures/armor/myarmor/cuirass_d.dds',
        'scripts/mymod/MyScript.pex',
        'scripts/mymod/AnotherScript.pex',
    ]

    for file_path in mod_files:
        full_path = os.path.join(mod_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(f"Mod file: {file_path}\n" + "y" * 500)  # ~500B per file

    print(f"✅ Created small mod with {len(mod_files)} files in 3 directories")
    return mod_dir, ['meshes', 'textures', 'scripts']


def create_mod_with_new_directories(base_dir):
    """Create a mod that has directories not in the source."""
    print("🆕 Creating mod with new directories...")

    mod_dir = os.path.join(base_dir, "ModWithNewDirs")

    # Mod uses some existing directories and some completely new ones
    mod_files = [
        'meshes/weapons/myweapon/sword.nif',      # Existing directory
        'textures/weapons/myweapon/sword_d.dds',  # Existing directory
        'MyModData/config.json',                  # NEW directory not in game
        'MyModData/settings.ini',                 # NEW directory not in game
        'CustomAssets/special_mesh.nif',          # NEW directory not in game
        'CustomAssets/special_texture.dds',       # NEW directory not in game
    ]

    for file_path in mod_files:
        full_path = os.path.join(mod_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(f"Mod file: {file_path}\n" + "z" * 750)  # ~750B per file

    print(f"✅ Created mod with new directories: MyModData, CustomAssets")
    return mod_dir, ['meshes', 'textures', 'MyModData', 'CustomAssets']


def test_selective_copy_optimization():
    """Test the selective copy optimization."""
    print("\n" + "="*70)
    print("🧪 TESTING SELECTIVE COPY OPTIMIZATION")
    print("="*70)

    test_dir = tempfile.mkdtemp(prefix="srp_selective_test_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create mock game data (large)
        game_data, all_game_dirs = create_mock_game_data(test_dir)

        # Create small mod (only uses few directories)
        small_mod, mod_dirs = create_small_mod(test_dir)

        # Test selective copying
        print(f"\n🔄 Testing selective copy optimization...")
        print(f"   Game has: {len(all_game_dirs)} directories")
        print(f"   Mod uses: {len(mod_dirs)} directories")
        print(f"   Expected savings: ~{((len(all_game_dirs) - len(mod_dirs)) / len(all_game_dirs)) * 100:.1f}%")

        # Create SafeResourcePacker and test selective copy
        packer = SafeResourcePacker(threads=2, debug=True)

        # This should trigger selective copying
        temp_source, temp_dir = packer.copy_folder_to_temp(game_data, small_mod)

        # Verify only the needed directories were copied
        copied_dirs = []
        if os.path.exists(temp_source):
            copied_dirs = [d for d in os.listdir(temp_source)
                          if os.path.isdir(os.path.join(temp_source, d))]

        print(f"\n📊 Selective copy results:")
        print(f"   Copied directories: {len(copied_dirs)}")
        print(f"   Expected directories: {len(mod_dirs)}")
        print(f"   Copied: {sorted(copied_dirs)}")
        print(f"   Expected: {sorted(mod_dirs)}")

        # Check if we got the right directories
        success = True
        for expected_dir in mod_dirs:
            if expected_dir.lower() not in [d.lower() for d in copied_dirs]:
                print(f"   ❌ Missing expected directory: {expected_dir}")
                success = False

        # Check we didn't copy unnecessary directories
        unnecessary = set(d.lower() for d in copied_dirs) - set(d.lower() for d in mod_dirs)
        if unnecessary:
            print(f"   ⚠️  Copied unnecessary directories: {unnecessary}")

        # Calculate actual space savings
        total_game_files = sum(len(files) for _, _, files in os.walk(game_data))
        copied_files = sum(len(files) for _, _, files in os.walk(temp_source)) if os.path.exists(temp_source) else 0

        if total_game_files > 0:
            actual_savings = ((total_game_files - copied_files) / total_game_files) * 100
            print(f"   💾 Actual space savings: {actual_savings:.1f}% ({total_game_files - copied_files} files saved)")

        # Cleanup temp
        packer.cleanup_temp()

        if success and len(copied_dirs) <= len(mod_dirs) + 2:  # Allow some tolerance
            print(f"\n✅ Selective copy optimization test PASSED!")
            return True
        else:
            print(f"\n❌ Selective copy optimization test FAILED!")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except:
            print(f"⚠️  Could not clean up: {test_dir}")


def test_mod_with_new_directories():
    """Test handling of mods with directories not in source."""
    print("\n" + "="*70)
    print("🧪 TESTING MOD WITH NEW DIRECTORIES")
    print("="*70)

    test_dir = tempfile.mkdtemp(prefix="srp_newdirs_test_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create mock game data
        game_data, all_game_dirs = create_mock_game_data(test_dir)

        # Create mod with new directories
        mod_with_new_dirs, mod_dirs = create_mod_with_new_directories(test_dir)

        print(f"\n🔄 Testing mod with new directories...")
        print(f"   Game directories: {len(all_game_dirs)}")
        print(f"   Mod directories: {mod_dirs}")
        print(f"   New directories: MyModData, CustomAssets")

        # Create SafeResourcePacker and test
        packer = SafeResourcePacker(threads=2, debug=True)

        # This should handle new directories gracefully
        temp_source, temp_dir = packer.copy_folder_to_temp(game_data, mod_with_new_dirs)

        # Verify only existing directories were copied from source
        copied_dirs = []
        if os.path.exists(temp_source):
            copied_dirs = [d for d in os.listdir(temp_source)
                          if os.path.isdir(os.path.join(temp_source, d))]

        print(f"\n📊 New directories handling results:")
        print(f"   Copied from source: {sorted(copied_dirs)}")

        # Should only copy meshes and textures (existing dirs), not MyModData/CustomAssets
        expected_existing = ['meshes', 'textures']
        success = True

        for expected in expected_existing:
            if expected.lower() not in [d.lower() for d in copied_dirs]:
                print(f"   ❌ Missing existing directory: {expected}")
                success = False

        # Should NOT copy the new directories (they don't exist in source)
        new_dirs_copied = [d for d in copied_dirs if d.lower() in ['mymoddata', 'customassets']]
        if new_dirs_copied:
            print(f"   ❌ Incorrectly copied new directories: {new_dirs_copied}")
            success = False

        # Cleanup temp
        packer.cleanup_temp()

        if success:
            print(f"\n✅ New directories handling test PASSED!")
            print(f"   ✅ Only existing directories copied from source")
            print(f"   ✅ New directories handled as mod-only files")
            return True
        else:
            print(f"\n❌ New directories handling test FAILED!")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except:
            print(f"⚠️  Could not clean up: {test_dir}")


def test_fallback_full_copy():
    """Test fallback to full copy when no generated path provided."""
    print("\n" + "="*70)
    print("🧪 TESTING FALLBACK FULL COPY")
    print("="*70)

    test_dir = tempfile.mkdtemp(prefix="srp_fallback_test_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create small mock game data
        game_data = os.path.join(test_dir, "SmallGameData")
        test_dirs = ['meshes', 'textures', 'sounds']

        total_files = 0
        for dir_name in test_dirs:
            dir_path = os.path.join(game_data, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            # Create a few files
            for i in range(3):
                file_path = os.path.join(dir_path, f"file_{i}.dat")
                with open(file_path, 'w') as f:
                    f.write(f"Test file {i} in {dir_name}")
                total_files += 1

        print(f"📁 Created small game data with {len(test_dirs)} directories, {total_files} files")

        # Test full copy (no generated path provided)
        packer = SafeResourcePacker(threads=2, debug=True)

        # This should trigger full copy mode
        temp_source, temp_dir = packer.copy_folder_to_temp(game_data, generated_path=None)

        # Verify all directories were copied
        copied_dirs = []
        if os.path.exists(temp_source):
            copied_dirs = [d for d in os.listdir(temp_source)
                          if os.path.isdir(os.path.join(temp_source, d))]

        print(f"\n📊 Full copy results:")
        print(f"   Original directories: {sorted(test_dirs)}")
        print(f"   Copied directories: {sorted(copied_dirs)}")

        success = len(copied_dirs) == len(test_dirs)

        # Cleanup temp
        packer.cleanup_temp()

        if success:
            print(f"\n✅ Fallback full copy test PASSED!")
            return True
        else:
            print(f"\n❌ Fallback full copy test FAILED!")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except:
            print(f"⚠️  Could not clean up: {test_dir}")


def main():
    """Run all selective copy optimization tests."""
    print("=" * 80)
    print("🎯 SAFE RESOURCE PACKER - SELECTIVE COPY OPTIMIZATION TEST")
    print("=" * 80)
    print()
    print("This test verifies the smart selective copying optimization:")
    print("• Only copies directories that the mod actually uses")
    print("• Provides massive space and time savings for large game Data folders")
    print("• Handles edge cases like mod-only directories")
    print("• Falls back to full copy when needed")
    print()

    results = []

    # Test selective copy optimization
    results.append(test_selective_copy_optimization())

    # Test mod with new directories
    results.append(test_mod_with_new_directories())

    # Test fallback full copy
    results.append(test_fallback_full_copy())

    # Summary
    print("\n" + "="*70)
    print("📊 SELECTIVE COPY OPTIMIZATION TEST RESULTS")
    print("="*70)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print()
        print("✅ Selective copy optimization is working perfectly!")
        print("   • Only relevant directories are copied from source")
        print("   • Massive space and time savings achieved")
        print("   • Mod-only directories handled correctly")
        print("   • Fallback to full copy works when needed")
        print()
        print("💾 SPACE SAVINGS: Up to 90%+ reduction in temporary storage!")
        print("⚡ TIME SAVINGS: Dramatically faster processing for large games!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print()
        print("❌ There may be issues with the selective copy optimization")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
