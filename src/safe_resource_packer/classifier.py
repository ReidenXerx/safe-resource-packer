"""
File classification logic for Safe Resource Packer.
"""

import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import log, print_progress, file_hash


class PathClassifier:
    """Handles file classification based on path matching and hash comparison."""

    def __init__(self, debug=False):
        """
        Initialize PathClassifier.

        Args:
            debug (bool): Enable debug logging
        """
        self.debug = debug
        self.skipped = []
        self.lock = threading.Lock()

    def find_file_case_insensitive(self, root, rel_path):
        """
        Find file with case-insensitive matching.

        Args:
            root (str): Root directory to search in
            rel_path (str): Relative path to find

        Returns:
            str or None: Full path to found file, or None if not found
        """
        parts = rel_path.replace('\\', '/').split('/')
        current = root
        for part in parts:
            try:
                match = next((f for f in os.listdir(current) if f.lower() == part.lower()), None)
                if match:
                    current = os.path.join(current, match)
                else:
                    return None
            except FileNotFoundError:
                return None
        return current

    def copy_file(self, src, rel_path, base_out):
        """
        Copy file to destination with error handling.

        Args:
            src (str): Source file path
            rel_path (str): Relative path for destination
            base_out (str): Base output directory

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            dest_path = os.path.join(base_out, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src, dest_path)
            return True
        except Exception as e:
            with self.lock:
                self.skipped.append(f"[COPY FAIL] {rel_path}: {e}")
            return False

    def process_file(self, source_root, out_pack, out_loose, gen_path, rel_path):
        """
        Process a single file and determine its classification.

        Args:
            source_root (str): Root of source files
            out_pack (str): Output directory for packable files
            out_loose (str): Output directory for loose files
            gen_path (str): Path to generated file
            rel_path (str): Relative path of file

        Returns:
            tuple: (result_type, relative_path)
        """
        try:
            src_path = self.find_file_case_insensitive(source_root, rel_path)
            if not src_path:
                log(f"[NO MATCH] {rel_path} → pack", debug_only=True)
                if self.copy_file(gen_path, rel_path, out_pack):
                    return 'pack', rel_path
            else:
                log(f"[MATCH FOUND] {rel_path} matched to {src_path}", debug_only=True)
                gen_hash = file_hash(gen_path)
                src_hash = file_hash(src_path)
                if gen_hash is None or src_hash is None:
                    return 'fail', rel_path
                if gen_hash == src_hash:
                    log(f"[SKIP] {rel_path} identical", debug_only=True)
                    return 'skip', rel_path
                else:
                    log(f"[OVERRIDE] {rel_path} differs", debug_only=True)
                    if self.copy_file(gen_path, rel_path, out_loose):
                        return 'loose', rel_path
            return 'fail', rel_path
        except Exception as e:
            with self.lock:
                self.skipped.append(f"[EXCEPTION] {rel_path}: {e}")
            return 'fail', rel_path

    def classify_by_path(self, source_root, generated_root, out_pack, out_loose, threads=8):
        """
        Classify all files in generated directory.

        Args:
            source_root (str): Root directory of source files
            generated_root (str): Root directory of generated files
            out_pack (str): Output directory for packable files
            out_loose (str): Output directory for loose files
            threads (int): Number of threads to use

        Returns:
            tuple: (pack_count, loose_count, skip_count)
        """
        # Reset skipped list for this classification run
        self.skipped = []

        all_gen_files = []
        for root, _, files in os.walk(generated_root):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, generated_root)
                all_gen_files.append((full_path, rel_path))

        total = len(all_gen_files)
        current = 0
        pack_count, loose_count, skip_count = 0, 0, 0

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(self.process_file, source_root, out_pack, out_loose, gp, rp)
                for gp, rp in all_gen_files
            ]
            for future in as_completed(futures):
                result, path = future.result()
                current += 1
                print_progress(current, total, "Classifying")
                if result == 'loose':
                    loose_count += 1
                elif result == 'pack':
                    pack_count += 1
                elif result == 'skip':
                    skip_count += 1
        print()
        return pack_count, loose_count, skip_count

    def get_skipped_files(self):
        """
        Get list of skipped files.

        Returns:
            list: List of skipped file messages
        """
        return self.skipped.copy()
