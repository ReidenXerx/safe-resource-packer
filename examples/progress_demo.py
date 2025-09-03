#!/usr/bin/env python3
"""
Progress Bar Demo - Shows the new temp file progress bars

This demo creates a temporary folder with many files to demonstrate
the progress bars for copying and cleaning up temporary files.
"""

import os
import sys
import tempfile
import shutil

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.core import SafeResourcePacker


def create_test_files(base_dir, num_files=150):
    """Create test files in nested directories."""
    print(f"📁 Creating {num_files} test files...")

    # Create nested structure
    subdirs = ['meshes', 'textures', 'sound', 'scripts']

    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)

        # Create files in each subdirectory
        files_per_dir = num_files // len(subdirs)
        for i in range(files_per_dir):
            file_path = os.path.join(subdir_path, f"{subdir}_file_{i:03d}.dat")
            with open(file_path, 'w') as f:
                f.write(f"Test content for {subdir} file {i}\n" * 10)  # Make files a bit larger

    print(f"✅ Created {num_files} test files in nested structure")


def main():
    """Demonstrate progress bars for temp file operations."""

    print("=" * 60)
    print("🎯 SAFE RESOURCE PACKER - PROGRESS BAR DEMO")
    print("=" * 60)
    print()
    print("This demo shows the new progress bars for:")
    print("• 📁 Copying source files to temporary directory")
    print("• 🧹 Cleaning up temporary files after processing")
    print()

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="srp_progress_demo_")
    print(f"📂 Test directory: {test_dir}")

    try:
        # Create many test files to trigger progress bars
        create_test_files(test_dir, 150)

        print("\n" + "="*50)
        print("🚀 TESTING PROGRESS BARS")
        print("="*50)

        # Initialize packer
        packer = SafeResourcePacker(threads=4, debug=False)

        print("\n1️⃣ Testing copy progress bar...")
        temp_source, temp_base = packer.copy_folder_to_temp(test_dir)

        print(f"\n✅ Copy completed!")
        print(f"   Source files copied to: {temp_source}")

        print("\n2️⃣ Testing cleanup progress bar...")
        packer.cleanup_temp()

        print("\n✅ Cleanup completed!")

        print("\n" + "="*50)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*50)
        print()
        print("💡 The progress bars will automatically appear when:")
        print("   • Processing folders with 100+ files")
        print("   • Rich library is available")
        print("   • Console UI or enhanced CLI is used")
        print()

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        # Clean up test directory
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")
        except:
            print(f"⚠️  Could not clean up test directory: {test_dir}")


if __name__ == "__main__":
    main()
