"""Tests for utility functions."""

import unittest
import tempfile
import os
import hashlib
from unittest.mock import patch, mock_open
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safe_resource_packer.utils import (
    log, print_progress, file_hash, write_log_file,
    get_logs, get_skipped, clear_logs, set_debug
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        clear_logs()
        set_debug(False)

    def tearDown(self):
        """Clean up after tests."""
        clear_logs()

    def test_log_basic(self):
        """Test basic logging functionality."""
        log("Test message")
        logs = get_logs()
        self.assertEqual(len(logs), 1)
        self.assertIn("Test message", logs[0])
        self.assertIn("[", logs[0])  # Should contain timestamp

    def test_log_debug_mode(self):
        """Test debug mode logging."""
        set_debug(False)
        log("Debug message", debug_only=True)
        logs = get_logs()
        self.assertEqual(len(logs), 0)  # Should not log debug messages

        set_debug(True)
        log("Debug message", debug_only=True)
        logs = get_logs()
        self.assertEqual(len(logs), 1)  # Should log debug messages

    def test_file_hash(self):
        """Test file hashing functionality."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            # Calculate hash
            hash_result = file_hash(temp_path)

            # Verify hash is correct
            expected_hash = hashlib.sha1(b"test content").hexdigest()
            self.assertEqual(hash_result, expected_hash)
        finally:
            os.unlink(temp_path)

    def test_file_hash_nonexistent(self):
        """Test file hashing with nonexistent file."""
        hash_result = file_hash("/nonexistent/file.txt")
        self.assertIsNone(hash_result)

        # Should have logged an error
        skipped = get_skipped()
        self.assertTrue(len(skipped) > 0)
        self.assertIn("HASH FAIL", skipped[0])

    def test_write_log_file(self):
        """Test log file writing."""
        log("Test message 1")
        log("Test message 2")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_log_path = f.name

        try:
            write_log_file(temp_log_path)

            # Read the log file and verify contents
            with open(temp_log_path, 'r') as f:
                content = f.read()
                self.assertIn("Test message 1", content)
                self.assertIn("Test message 2", content)
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)

    def test_clear_logs(self):
        """Test log clearing functionality."""
        log("Test message")
        self.assertTrue(len(get_logs()) > 0)

        clear_logs()
        self.assertEqual(len(get_logs()), 0)
        self.assertEqual(len(get_skipped()), 0)


class TestPrintProgress(unittest.TestCase):
    """Test progress printing functionality."""

    @patch('sys.stdout')
    def test_print_progress(self, mock_stdout):
        """Test progress bar printing."""
        print_progress(50, 100, "Testing")

        # Should have written to stdout
        mock_stdout.write.assert_called()
        mock_stdout.flush.assert_called()

        # Get the written content
        written_content = mock_stdout.write.call_args[0][0]
        self.assertIn("50.0%", written_content)
        self.assertIn("Testing", written_content)
        self.assertIn("[", written_content)  # Progress bar


if __name__ == '__main__':
    unittest.main()
