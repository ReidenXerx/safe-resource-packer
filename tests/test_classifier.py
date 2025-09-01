"""Tests for file classification functionality."""

import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer.classifier import PathClassifier


class TestPathClassifier(unittest.TestCase):
    """Test path classification functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = PathClassifier(debug=True)

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
        shutil.rmtree(self.test_dir)

    def create_test_file(self, directory, filename, content="test content"):
        """Create a test file with specified content."""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def test_find_file_case_insensitive(self):
        """Test case-insensitive file finding."""
        # Create a file with specific case
        self.create_test_file(self.source_dir, "TestFile.txt")

        # Should find file regardless of case
        found = self.classifier.find_file_case_insensitive(self.source_dir, "testfile.txt")
        self.assertIsNotNone(found)
        self.assertTrue(os.path.exists(found))

        found = self.classifier.find_file_case_insensitive(self.source_dir, "TESTFILE.TXT")
        self.assertIsNotNone(found)

        # Should return None for non-existent files
        found = self.classifier.find_file_case_insensitive(self.source_dir, "nonexistent.txt")
        self.assertIsNone(found)

    def test_find_file_nested_path(self):
        """Test finding files in nested directories."""
        # Create nested file structure
        nested_file = "subdir/nested/file.txt"
        self.create_test_file(self.source_dir, nested_file)

        # Should find with exact case
        found = self.classifier.find_file_case_insensitive(self.source_dir, nested_file)
        self.assertIsNotNone(found)

        # Should find with different case
        found = self.classifier.find_file_case_insensitive(self.source_dir, "SUBDIR/NESTED/FILE.TXT")
        self.assertIsNotNone(found)

        # Should find with mixed case
        found = self.classifier.find_file_case_insensitive(self.source_dir, "SubDir/Nested/File.txt")
        self.assertIsNotNone(found)

    def test_copy_file(self):
        """Test file copying functionality."""
        # Create source file
        source_file = self.create_test_file(self.test_dir, "source_file.txt", "test content")

        # Copy file
        success = self.classifier.copy_file(source_file, "copied_file.txt", self.pack_dir)
        self.assertTrue(success)

        # Verify file was copied
        copied_file = os.path.join(self.pack_dir, "copied_file.txt")
        self.assertTrue(os.path.exists(copied_file))

        with open(copied_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "test content")

    def test_copy_file_nested_path(self):
        """Test copying file to nested directory."""
        # Create source file
        source_file = self.create_test_file(self.test_dir, "source_file.txt", "test content")

        # Copy to nested path
        nested_path = "sub/dir/copied_file.txt"
        success = self.classifier.copy_file(source_file, nested_path, self.pack_dir)
        self.assertTrue(success)

        # Verify file was copied to correct location
        copied_file = os.path.join(self.pack_dir, nested_path)
        self.assertTrue(os.path.exists(copied_file))

    def test_process_file_new_file(self):
        """Test processing a file that doesn't exist in source."""
        # Create generated file only
        gen_file = self.create_test_file(self.generated_dir, "new_file.txt", "new content")

        result, path = self.classifier.process_file(
            self.source_dir, self.pack_dir, self.loose_dir, gen_file, "new_file.txt"
        )

        self.assertEqual(result, 'pack')
        self.assertEqual(path, "new_file.txt")

        # Verify file was copied to pack directory
        packed_file = os.path.join(self.pack_dir, "new_file.txt")
        self.assertTrue(os.path.exists(packed_file))

    def test_process_file_identical_files(self):
        """Test processing identical files."""
        # Create identical files in both directories
        content = "identical content"
        self.create_test_file(self.source_dir, "identical.txt", content)
        gen_file = self.create_test_file(self.generated_dir, "identical.txt", content)

        result, path = self.classifier.process_file(
            self.source_dir, self.pack_dir, self.loose_dir, gen_file, "identical.txt"
        )

        self.assertEqual(result, 'skip')
        self.assertEqual(path, "identical.txt")

        # Verify no files were copied
        self.assertFalse(os.path.exists(os.path.join(self.pack_dir, "identical.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.loose_dir, "identical.txt")))

    def test_process_file_different_files(self):
        """Test processing different files (overrides)."""
        # Create different files
        self.create_test_file(self.source_dir, "modified.txt", "original content")
        gen_file = self.create_test_file(self.generated_dir, "modified.txt", "modified content")

        result, path = self.classifier.process_file(
            self.source_dir, self.pack_dir, self.loose_dir, gen_file, "modified.txt"
        )

        self.assertEqual(result, 'loose')
        self.assertEqual(path, "modified.txt")

        # Verify file was copied to loose directory
        loose_file = os.path.join(self.loose_dir, "modified.txt")
        self.assertTrue(os.path.exists(loose_file))

        with open(loose_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "modified content")

    def test_classify_by_path_mixed_files(self):
        """Test classification with mixed file scenarios."""
        # Create test files
        # 1. New file (should go to pack)
        self.create_test_file(self.generated_dir, "new_file.txt", "new")

        # 2. Identical file (should be skipped)
        identical_content = "same content"
        self.create_test_file(self.source_dir, "identical.txt", identical_content)
        self.create_test_file(self.generated_dir, "identical.txt", identical_content)

        # 3. Modified file (should go to loose)
        self.create_test_file(self.source_dir, "modified.txt", "original")
        self.create_test_file(self.generated_dir, "modified.txt", "changed")

        # Run classification
        pack_count, loose_count, skip_count = self.classifier.classify_by_path(
            self.source_dir, self.generated_dir, self.pack_dir, self.loose_dir, threads=1
        )

        # Verify counts
        self.assertEqual(pack_count, 1)   # new_file.txt
        self.assertEqual(loose_count, 1)  # modified.txt
        self.assertEqual(skip_count, 1)   # identical.txt

        # Verify files are in correct locations
        self.assertTrue(os.path.exists(os.path.join(self.pack_dir, "new_file.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.loose_dir, "modified.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.pack_dir, "identical.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.loose_dir, "identical.txt")))


if __name__ == '__main__':
    unittest.main()
