"""Tests for core functionality."""

import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer.core import SafeResourcePacker


class TestSafeResourcePacker(unittest.TestCase):
    """Test core SafeResourcePacker functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.packer = SafeResourcePacker(threads=2, debug=True)

        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source")
        self.generated_dir = os.path.join(self.test_dir, "generated")
        self.pack_dir = os.path.join(self.test_dir, "pack")
        self.loose_dir = os.path.join(self.test_dir, "loose")

        os.makedirs(self.source_dir)
        os.makedirs(self.generated_dir)
        os.makedirs(self.pack_dir)
        os.makedirs(self.loose_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        self.packer.cleanup_temp()
        shutil.rmtree(self.test_dir)

    def create_test_file(self, directory, filename, content="test content"):
        """Create a test file with specified content."""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def test_copy_folder_to_temp(self):
        """Test copying source folder to temporary location."""
        # Create some test files in source
        self.create_test_file(self.source_dir, "file1.txt", "content1")
        self.create_test_file(self.source_dir, "subdir/file2.txt", "content2")

        # Copy to temp
        temp_source, temp_dir = self.packer.copy_folder_to_temp(self.source_dir)

        try:
            # Verify temp directory was created
            self.assertTrue(os.path.exists(temp_dir))
            self.assertTrue(os.path.exists(temp_source))

            # Verify files were copied
            self.assertTrue(os.path.exists(os.path.join(temp_source, "file1.txt")))
            self.assertTrue(os.path.exists(os.path.join(temp_source, "subdir/file2.txt")))

            # Verify content is correct
            with open(os.path.join(temp_source, "file1.txt"), 'r') as f:
                self.assertEqual(f.read(), "content1")
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_process_resources(self):
        """Test end-to-end resource processing."""
        # Create test files
        # 1. New file (should go to pack)
        self.create_test_file(self.generated_dir, "new_file.txt", "new content")

        # 2. Identical file (should be skipped)
        identical_content = "same content"
        self.create_test_file(self.source_dir, "identical.txt", identical_content)
        self.create_test_file(self.generated_dir, "identical.txt", identical_content)

        # 3. Modified file (should go to loose)
        self.create_test_file(self.source_dir, "modified.txt", "original content")
        self.create_test_file(self.generated_dir, "modified.txt", "modified content")

        # Process resources
        pack_count, loose_count, skip_count = self.packer.process_resources(
            self.source_dir, self.generated_dir, self.pack_dir, self.loose_dir
        )

        # Verify results
        self.assertEqual(pack_count, 1)   # new_file.txt
        self.assertEqual(loose_count, 1)  # modified.txt
        self.assertEqual(skip_count, 1)   # identical.txt

        # Verify files are in correct locations
        self.assertTrue(os.path.exists(os.path.join(self.pack_dir, "new_file.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.loose_dir, "modified.txt")))

        # Verify file contents
        with open(os.path.join(self.pack_dir, "new_file.txt"), 'r') as f:
            self.assertEqual(f.read(), "new content")

        with open(os.path.join(self.loose_dir, "modified.txt"), 'r') as f:
            self.assertEqual(f.read(), "modified content")

    def test_cleanup_temp(self):
        """Test temporary directory cleanup."""
        # Create temp directory
        temp_source, temp_dir = self.packer.copy_folder_to_temp(self.source_dir)

        # Verify it exists
        self.assertTrue(os.path.exists(temp_dir))

        # Cleanup
        self.packer.cleanup_temp()

        # Verify it's gone
        self.assertFalse(os.path.exists(temp_dir))
        self.assertIsNone(self.packer.temp_dir)

    def test_initialization(self):
        """Test SafeResourcePacker initialization."""
        packer = SafeResourcePacker(threads=16, debug=False)

        self.assertEqual(packer.threads, 16)
        self.assertEqual(packer.debug, False)
        self.assertIsNotNone(packer.classifier)
        self.assertIsNone(packer.temp_dir)


if __name__ == '__main__':
    unittest.main()
