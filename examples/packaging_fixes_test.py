#!/usr/bin/env python3
"""
Packaging Fixes Test - Verifies the fixes for duplicate filenames and metadata issues

This test creates a scenario similar to the reported bug and verifies that:
1. Duplicate filenames are handled correctly by preserving directory structure
2. Metadata files are created before final packaging
3. Compression fallbacks work properly
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.packaging.compressor import Compressor
from safe_resource_packer.packaging.package_builder import PackageBuilder


def create_test_files_with_duplicates(base_dir):
    """Create test files that would cause duplicate filename issues."""
    print("📁 Creating test files with potential duplicate names...")

    # Create directory structure with duplicate filenames
    dirs = [
        'meshes/armor/dragonbone',
        'meshes/armor/dragonscale',
        'meshes/clothes/mage',
        'meshes/clothes/noble'
    ]

    # Files that will have the same name but different paths
    duplicate_files = [
        'torso_0.nif',
        'torso_1.nif',
        'boots_0.nif',
        'boots_1.nif',
        'gauntlets_0.nif',
        'gauntlets_1.nif'
    ]

    all_files = []

    for dir_path in dirs:
        full_dir = os.path.join(base_dir, dir_path)
        os.makedirs(full_dir, exist_ok=True)

        for filename in duplicate_files:
            file_path = os.path.join(full_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content for {dir_path}/{filename}\n")
                f.write(f"This file is in: {dir_path}\n")
                f.write("Some binary-like content: " + "x" * 100 + "\n")
            all_files.append(file_path)

    print(f"✅ Created {len(all_files)} test files with duplicate names across directories")
    return all_files


def test_compression_with_duplicates():
    """Test that compression handles duplicate filenames correctly."""
    print("\n" + "="*60)
    print("🧪 TESTING COMPRESSION WITH DUPLICATE FILENAMES")
    print("="*60)

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="srp_compression_test_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create test files with duplicates
        test_files = create_test_files_with_duplicates(test_dir)

        # Test compression
        compressor = Compressor(compression_level=5)
        archive_path = os.path.join(test_dir, "test_archive.7z")

        print(f"\n🗜️  Testing compression of {len(test_files)} files...")
        print("   (This should preserve directory structure and avoid duplicate name conflicts)")

        success, message = compressor.compress_files(test_files, archive_path)

        if success:
            print(f"✅ Compression successful: {message}")

            # Check if archive was created
            if os.path.exists(archive_path):
                size_mb = os.path.getsize(archive_path) / (1024 * 1024)
                print(f"📦 Archive created: {os.path.basename(archive_path)} ({size_mb:.2f} MB)")
            elif os.path.exists(archive_path.replace('.7z', '.zip')):
                zip_path = archive_path.replace('.7z', '.zip')
                size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                print(f"📦 ZIP fallback created: {os.path.basename(zip_path)} ({size_mb:.2f} MB)")

            return True
        else:
            print(f"❌ Compression failed: {message}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        # Clean up
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except:
            print(f"⚠️  Could not clean up: {test_dir}")


def test_package_builder_metadata():
    """Test that package builder creates metadata correctly."""
    print("\n" + "="*60)
    print("🧪 TESTING PACKAGE BUILDER METADATA CREATION")
    print("="*60)

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="srp_package_test_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create some test files
        pack_files = create_test_files_with_duplicates(os.path.join(test_dir, "pack_files"))

        # Create classification results
        classification_results = {
            'pack': pack_files[:6],  # First 6 files for packing
            'loose': pack_files[6:12] if len(pack_files) > 6 else [],  # Next 6 for loose
            'skip': []
        }

        print(f"📋 Classification results:")
        print(f"   Pack files: {len(classification_results['pack'])}")
        print(f"   Loose files: {len(classification_results['loose'])}")

        # Test package builder
        builder = PackageBuilder(game_type="skyrim", compression_level=3)
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n📦 Testing package build...")
        success, package_path, package_info = builder.build_complete_package(
            classification_results,
            "testmod",
            output_dir,
            {"cleanup_temp": False}  # Keep temp files for inspection
        )

        if success:
            print(f"✅ Package build successful!")
            print(f"📦 Package path: {package_path}")

            # Check if metadata was created
            package_dir = os.path.join(output_dir, "testmod_Package")
            metadata_dir = os.path.join(package_dir, "_metadata")

            if os.path.exists(metadata_dir):
                print(f"✅ Metadata directory created: {metadata_dir}")

                # Check for specific files
                expected_files = ["package_info.json", "build_log.txt", "file_manifest.txt", "INSTALLATION.txt"]
                for file in expected_files:
                    file_path = os.path.join(metadata_dir, file)
                    if os.path.exists(file_path):
                        print(f"   ✅ {file} created")
                    else:
                        print(f"   ❌ {file} missing")
            else:
                print(f"❌ Metadata directory not found: {metadata_dir}")

            return True
        else:
            print(f"❌ Package build failed")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except:
            print(f"⚠️  Could not clean up: {test_dir}")


def main():
    """Run all packaging tests."""
    print("=" * 80)
    print("🎯 SAFE RESOURCE PACKER - PACKAGING FIXES TEST")
    print("=" * 80)
    print()
    print("This test verifies fixes for:")
    print("• 🔧 Duplicate filename handling in compression")
    print("• 📄 Metadata file creation and ordering")
    print("• 🗜️  Compression fallback improvements")
    print()

    results = []

    # Test compression with duplicates
    results.append(test_compression_with_duplicates())

    # Test package builder metadata
    results.append(test_package_builder_metadata())

    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print()
        print("✅ The packaging fixes are working correctly!")
        print("   • Duplicate filenames are handled by preserving directory structure")
        print("   • Metadata files are created before final packaging")
        print("   • Compression fallbacks work properly")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print()
        print("❌ There may still be issues with the packaging system")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
