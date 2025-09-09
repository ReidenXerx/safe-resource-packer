#!/usr/bin/env python3
"""
Data Integrity Test for Multithreaded py7zr Compression

This test verifies that NO FILES ARE LOST during the multithreaded compression process.
It creates test files with known content, compresses them, extracts the archive,
and verifies that every single file is present and identical.

Test Coverage:
- File count verification (no files lost)
- Content integrity verification (no corruption)
- Directory structure preservation
- Edge cases (empty files, large files, special characters)
- Stress testing with many files
"""

import os
import sys
import time
import tempfile
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Set

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.packaging.compressor import Compressor
from safe_resource_packer.utils import log, set_debug

try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    PY7ZR_AVAILABLE = False
    print("⚠️  py7zr not available - installing...")


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"❌ Failed to hash {file_path}: {e}")
        return ""


def create_test_dataset(test_dir: str) -> Dict[str, str]:
    """Create a comprehensive test dataset with known content and return file hashes."""
    print(f"📁 Creating comprehensive test dataset in {test_dir}...")
    
    file_hashes = {}
    
    # Test case 1: Regular files with different sizes
    regular_dir = os.path.join(test_dir, "regular_files")
    os.makedirs(regular_dir, exist_ok=True)
    
    for i in range(100):
        file_path = os.path.join(regular_dir, f"regular_file_{i:03d}.txt")
        content = f"Regular file {i}\n" + "Data line " * (i + 1) + f"\nEnd of file {i}\n"
        with open(file_path, 'w') as f:
            f.write(content)
        file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
    
    # Test case 2: Empty files
    empty_dir = os.path.join(test_dir, "empty_files")
    os.makedirs(empty_dir, exist_ok=True)
    
    for i in range(10):
        file_path = os.path.join(empty_dir, f"empty_file_{i:03d}.txt")
        with open(file_path, 'w') as f:
            pass  # Create empty file
        file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
    
    # Test case 3: Large files
    large_dir = os.path.join(test_dir, "large_files")
    os.makedirs(large_dir, exist_ok=True)
    
    for i in range(5):
        file_path = os.path.join(large_dir, f"large_file_{i:03d}.bin")
        with open(file_path, 'wb') as f:
            # Create 1MB file with known pattern
            pattern = bytes([i % 256] * 1024)  # 1KB pattern
            for _ in range(1024):  # Write 1MB
                f.write(pattern)
        file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
    
    # Test case 4: Files with special characters in names
    special_dir = os.path.join(test_dir, "special_names")
    os.makedirs(special_dir, exist_ok=True)
    
    special_names = [
        "file with spaces.txt",
        "file-with-dashes.txt",
        "file_with_underscores.txt",
        "file.with.dots.txt",
        "file(with)parentheses.txt",
        "file[with]brackets.txt",
        "файл_кириллица.txt",  # Cyrillic
        "文件_中文.txt",  # Chinese
    ]
    
    for i, name in enumerate(special_names):
        try:
            file_path = os.path.join(special_dir, name)
            content = f"Special file {i}: {name}\nContent with special characters: éñ中文\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
        except Exception as e:
            print(f"⚠️  Skipped special file {name}: {e}")
    
    # Test case 5: Deep directory structure
    deep_base = os.path.join(test_dir, "deep_structure")
    for depth in range(5):
        deep_dir = os.path.join(deep_base, *[f"level_{i}" for i in range(depth + 1)])
        os.makedirs(deep_dir, exist_ok=True)
        
        for i in range(3):
            file_path = os.path.join(deep_dir, f"deep_file_d{depth}_f{i}.txt")
            content = f"Deep file at depth {depth}, file {i}\n" + "x" * (depth * 100 + i * 50)
            with open(file_path, 'w') as f:
                f.write(content)
            file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
    
    # Test case 6: Many small files (stress test)
    stress_dir = os.path.join(test_dir, "stress_test")
    os.makedirs(stress_dir, exist_ok=True)
    
    for i in range(200):
        subdir = os.path.join(stress_dir, f"batch_{i // 20}")
        os.makedirs(subdir, exist_ok=True)
        
        file_path = os.path.join(subdir, f"stress_file_{i:04d}.txt")
        content = f"Stress test file {i}\n" + str(i) * 10 + "\n"
        with open(file_path, 'w') as f:
            f.write(content)
        file_hashes[os.path.relpath(file_path, test_dir)] = calculate_file_hash(file_path)
    
    total_files = len(file_hashes)
    print(f"✅ Created {total_files} test files with known hashes")
    return file_hashes


def extract_and_verify_archive(archive_path: str, extract_dir: str, expected_hashes: Dict[str, str]) -> bool:
    """Extract archive and verify all files are present and identical."""
    print(f"📦 Extracting and verifying archive: {archive_path}")
    
    try:
        # Extract the archive
        with py7zr.SevenZipFile(archive_path, 'r') as archive:
            archive.extractall(path=extract_dir)
        
        print(f"✅ Archive extracted to: {extract_dir}")
        
        # Verify file count
        extracted_files = {}
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extract_dir)
                extracted_files[rel_path] = calculate_file_hash(file_path)
        
        extracted_count = len(extracted_files)
        expected_count = len(expected_hashes)
        
        print(f"📊 File count check: Expected {expected_count}, Found {extracted_count}")
        
        if extracted_count != expected_count:
            print(f"❌ FILE COUNT MISMATCH!")
            
            # Find missing files
            missing_files = set(expected_hashes.keys()) - set(extracted_files.keys())
            if missing_files:
                print(f"❌ Missing files ({len(missing_files)}):")
                for missing in sorted(missing_files):
                    print(f"   - {missing}")
            
            # Find extra files
            extra_files = set(extracted_files.keys()) - set(expected_hashes.keys())
            if extra_files:
                print(f"⚠️  Extra files ({len(extra_files)}):")
                for extra in sorted(extra_files):
                    print(f"   + {extra}")
            
            return False
        
        # Verify file content integrity
        print("🔍 Verifying file content integrity...")
        corrupted_files = []
        
        for rel_path, expected_hash in expected_hashes.items():
            if rel_path in extracted_files:
                actual_hash = extracted_files[rel_path]
                if actual_hash != expected_hash:
                    corrupted_files.append(rel_path)
                    print(f"❌ CORRUPTED: {rel_path}")
                    print(f"   Expected: {expected_hash}")
                    print(f"   Actual:   {actual_hash}")
            else:
                print(f"❌ MISSING: {rel_path}")
                return False
        
        if corrupted_files:
            print(f"❌ CONTENT CORRUPTION DETECTED in {len(corrupted_files)} files!")
            return False
        
        print(f"✅ All {extracted_count} files verified successfully - NO DATA LOSS!")
        return True
        
    except Exception as e:
        print(f"💥 Archive extraction/verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_integrity():
    """Comprehensive data integrity test for multithreaded compression."""
    print("🔒 Data Integrity Test for Multithreaded py7zr Compression")
    print("=" * 60)
    
    if not PY7ZR_AVAILABLE:
        print("❌ py7zr not available - cannot run integrity test")
        return False
    
    # Enable debug for detailed logging
    set_debug(True)
    
    with tempfile.TemporaryDirectory(prefix="integrity_test_") as temp_dir:
        test_data_dir = os.path.join(temp_dir, "test_data")
        extract_dir = os.path.join(temp_dir, "extracted")
        archive_path = os.path.join(temp_dir, "integrity_test.7z")
        
        os.makedirs(test_data_dir)
        os.makedirs(extract_dir)
        
        print(f"🏗️  Test directory: {temp_dir}")
        
        # Step 1: Create comprehensive test dataset
        print("\n📋 Step 1: Creating test dataset...")
        expected_hashes = create_test_dataset(test_data_dir)
        
        if not expected_hashes:
            print("❌ Failed to create test dataset")
            return False
        
        # Step 2: Compress using multithreaded py7zr
        print(f"\n🗜️  Step 2: Compressing {len(expected_hashes)} files...")
        
        compressor = Compressor(compression_level=5)  # Balanced compression
        start_time = time.time()
        
        try:
            success, message = compressor._compress_directory_with_py7zr(test_data_dir, archive_path)
            compression_time = time.time() - start_time
            
            if not success:
                print(f"❌ Compression failed: {message}")
                return False
            
            if not os.path.exists(archive_path):
                print(f"❌ Archive not created: {archive_path}")
                return False
            
            archive_size = os.path.getsize(archive_path) / (1024 * 1024)  # MB
            print(f"✅ Compression successful: {archive_size:.1f}MB in {compression_time:.1f}s")
            
        except Exception as e:
            print(f"💥 Compression error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 3: Extract and verify
        print(f"\n🔍 Step 3: Extracting and verifying archive...")
        
        verification_success = extract_and_verify_archive(archive_path, extract_dir, expected_hashes)
        
        if verification_success:
            print(f"\n🎉 DATA INTEGRITY TEST PASSED!")
            print(f"   ✅ All {len(expected_hashes)} files preserved")
            print(f"   ✅ No data corruption detected")
            print(f"   ✅ Directory structure maintained")
            print(f"   ✅ Special characters handled correctly")
            print(f"   ✅ Multithreaded compression is SAFE!")
        else:
            print(f"\n💥 DATA INTEGRITY TEST FAILED!")
            print(f"   ❌ Files were lost or corrupted during compression!")
        
        return verification_success


def stress_test_data_integrity():
    """Stress test with many files to ensure robustness."""
    print("\n🏋️  Stress Test: Data Integrity with Large Dataset")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory(prefix="stress_integrity_") as temp_dir:
        test_data_dir = os.path.join(temp_dir, "stress_data")
        extract_dir = os.path.join(temp_dir, "stress_extracted")
        archive_path = os.path.join(temp_dir, "stress_test.7z")
        
        os.makedirs(test_data_dir)
        os.makedirs(extract_dir)
        
        # Create a large number of files for stress testing
        print("📁 Creating 1000 test files for stress testing...")
        
        file_hashes = {}
        for i in range(1000):
            subdir = os.path.join(test_data_dir, f"batch_{i // 100}")
            os.makedirs(subdir, exist_ok=True)
            
            file_path = os.path.join(subdir, f"stress_{i:04d}.txt")
            content = f"Stress file {i}\n" + str(i % 100) * 50 + f"\nChecksum: {i * 12345}\n"
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            file_hashes[os.path.relpath(file_path, test_data_dir)] = calculate_file_hash(file_path)
        
        print(f"✅ Created {len(file_hashes)} stress test files")
        
        # Compress with multithreading
        print("🗜️  Compressing with maximum multithreading...")
        set_debug(False)  # Reduce logging for stress test
        
        compressor = Compressor(compression_level=3)  # Fast compression for stress test
        start_time = time.time()
        
        success, message = compressor._compress_directory_with_py7zr(test_data_dir, archive_path)
        compression_time = time.time() - start_time
        
        if success:
            archive_size = os.path.getsize(archive_path) / (1024 * 1024)
            files_per_sec = len(file_hashes) / compression_time
            print(f"✅ Stress compression: {archive_size:.1f}MB in {compression_time:.1f}s ({files_per_sec:.1f} files/sec)")
            
            # Verify integrity
            verification_success = extract_and_verify_archive(archive_path, extract_dir, file_hashes)
            
            if verification_success:
                print("🎉 STRESS TEST PASSED - No data loss with 1000 files!")
            else:
                print("💥 STRESS TEST FAILED - Data integrity compromised!")
            
            return verification_success
        else:
            print(f"❌ Stress test compression failed: {message}")
            return False


def main():
    """Run comprehensive data integrity tests."""
    print("🛡️  Safe Resource Packer - Data Integrity Verification")
    print("=====================================================")
    print("This test ensures NO FILES ARE LOST during multithreaded compression!")
    print()
    
    try:
        # Test 1: Comprehensive data integrity
        test1_passed = test_data_integrity()
        
        if test1_passed:
            # Test 2: Stress test with many files
            test2_passed = stress_test_data_integrity()
            
            if test2_passed:
                print("\n🏆 ALL TESTS PASSED!")
                print("✅ Multithreaded py7zr compression is SAFE and RELIABLE!")
                print("✅ No files are lost during the compression process!")
                print("✅ All file content is preserved with 100% integrity!")
                print("\n💡 You can confidently use multithreaded compression!")
                return True
            else:
                print("\n⚠️  Stress test failed - multithreaded compression may have issues with large datasets")
                return False
        else:
            print("\n❌ Basic integrity test failed - multithreaded compression is NOT SAFE!")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
