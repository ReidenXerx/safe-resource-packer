"""
Core functionality for Safe Resource Packer.
"""

import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from .classifier import PathClassifier
from .utils import log, print_progress


class SafeResourcePacker:
    """Main class for safe resource packing operations."""

    def __init__(self, threads=8, debug=False):
        """
        Initialize SafeResourcePacker.

        Args:
            threads (int): Number of threads to use for processing
            debug (bool): Enable debug logging
        """
        self.threads = threads
        self.debug = debug
        self.classifier = PathClassifier(debug=debug)
        self.temp_dir = None

    def copy_folder_to_temp(self, source):
        """
        Copy source folder to temporary directory for safe processing.

        Args:
            source (str): Path to source directory

        Returns:
            tuple: (temp_source_path, temp_directory)
        """
        self.temp_dir = tempfile.mkdtemp()
        log(f"Copying source to temp directory: {self.temp_dir}")
        shutil.copytree(source, os.path.join(self.temp_dir, 'source'), dirs_exist_ok=True)
        return os.path.join(self.temp_dir, 'source'), self.temp_dir

    def process_resources(self, source_path, generated_path, output_pack, output_loose):
        """
        Process resources and classify them for packing or loose deployment.

        Args:
            source_path (str): Path to source/reference files
            generated_path (str): Path to generated/modified files
            output_pack (str): Path for files safe to pack
            output_loose (str): Path for files that should remain loose

        Returns:
            tuple: (pack_count, loose_count, skip_count)
        """
        # Create temporary copy of source for safe processing
        real_source, temp_dir = self.copy_folder_to_temp(source_path)

        try:
            log("Classifying generated files by path override logic...")
            return self.classifier.classify_by_path(
                real_source, generated_path, output_pack, output_loose, self.threads
            )
        finally:
            self.cleanup_temp()

    def cleanup_temp(self):
        """Clean up temporary directories."""
        if self.temp_dir:
            try:
                shutil.rmtree(self.temp_dir)
                log(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                log(f"Failed to clean temp directory: {e}")
            finally:
                self.temp_dir = None
