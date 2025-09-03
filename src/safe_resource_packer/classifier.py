"""
File classification logic for Safe Resource Packer.
"""

import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import log, print_progress, file_hash
from .game_scanner import get_game_scanner


class PathClassifier:
    """Handles file classification based on path matching and hash comparison."""

    def __init__(self, debug=False, game_path=None, game_type="skyrim"):
        """
        Initialize PathClassifier.

        Args:
            debug (bool): Enable debug logging
            game_path (str): Path to game installation for directory scanning
            game_type (str): Type of game ("skyrim" or "fallout4")
        """
        self.debug = debug
        self.game_path = game_path
        self.game_type = game_type.lower()
        self.skipped = []
        self.lock = threading.Lock()

        # Initialize game scanner and get real directories
        self.game_scanner = get_game_scanner()
        self.game_directories = None
        if self.game_path:
            self.game_directories = self.game_scanner.scan_game_data_directory(
                self.game_path, self.game_type
            )

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
        Copy file to destination with error handling and proper game directory structure.d k t

        Args:
            src (str): Source file path
            rel_path (str): Relative path for destination
            base_out (str): Base output directory

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract proper Data-relative path to maintain game directory structure
            data_rel_path = self._extract_data_relative_path(src)
            dest_path = os.path.join(base_out, data_rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src, dest_path)
            log(f"Copied with Data structure: {src} → {data_rel_path}", debug_only=True, log_type='INFO')
            return True
        except Exception as e:
            with self.lock:
                self.skipped.append(f"[COPY FAIL] {rel_path}: {e}")
            log(f"[COPY FAIL] {rel_path}: {e}", debug_only=True, log_type='COPY FAIL')
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
            # Get the proper Data-relative path for this file
            data_rel_path = self._extract_data_relative_path(gen_path)

            src_path = self.find_file_case_insensitive(source_root, rel_path)
            if not src_path:
                log(f"[NO MATCH] {rel_path} → pack", debug_only=True, log_type='NO MATCH')
                if self.copy_file(gen_path, rel_path, out_pack):
                    return 'pack', data_rel_path
            else:
                log(f"[MATCH FOUND] {rel_path} matched to {src_path}", debug_only=True, log_type='MATCH FOUND')
                gen_hash = file_hash(gen_path)
                src_hash = file_hash(src_path)
                if gen_hash is None or src_hash is None:
                    return 'fail', data_rel_path
                if gen_hash == src_hash:
                    log(f"[SKIP] {rel_path} identical", debug_only=True, log_type='SKIP')
                    return 'skip', data_rel_path
                else:
                    log(f"[OVERRIDE] {rel_path} differs", debug_only=True, log_type='OVERRIDE')
                    if self.copy_file(gen_path, rel_path, out_loose):
                        return 'loose', data_rel_path
            return 'fail', data_rel_path
        except Exception as e:
            with self.lock:
                self.skipped.append(f"[EXCEPTION] {rel_path}: {e}")
            log(f"[EXCEPTION] {rel_path}: {e}", debug_only=True, log_type='EXCEPTION')
            return 'fail', rel_path

    def classify_by_path(self, source_root, generated_root, out_pack, out_loose, threads=8, progress_callback=None):
        """
        Classify all files in generated directory.

        Args:
            source_root (str): Root directory of source files
            generated_root (str): Root directory of generated files
            out_pack (str): Output directory for packable files
            out_loose (str): Output directory for loose files
            threads (int): Number of threads to use
            progress_callback (callable): Optional callback for progress updates

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

        # Initialize progress callback if it's a CleanOutputManager
        if hasattr(progress_callback, 'start_processing'):
            progress_callback.start_processing(total)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(self.process_file, source_root, out_pack, out_loose, gp, rp)
                for gp, rp in all_gen_files
            ]
            for future in as_completed(futures):
                result, path = future.result()
                current += 1

                # Update progress with clean callback
                if hasattr(progress_callback, 'update_progress'):
                    progress_callback.update_progress(path, result)
                elif progress_callback:
                    progress_callback(current, total, "Classifying", path)
                else:
                    print_progress(current, total, "Classifying", path)

                if result == 'loose':
                    loose_count += 1
                elif result == 'pack':
                    pack_count += 1
                elif result == 'skip':
                    skip_count += 1

        # Finish progress callback if it's a CleanOutputManager
        if hasattr(progress_callback, 'finish_processing'):
            progress_callback.finish_processing()
        print()
        return pack_count, loose_count, skip_count

    def get_skipped_files(self):
        """
        Get list of skipped files.

        Returns:
            list: List of skipped file messages
        """
        return self.skipped.copy()

    def _extract_data_relative_path(self, file_path: str) -> str:
        """
        Extract Data-relative path using bulletproof approach with real game directories.

        This is much simpler than the old approach - we just look for the first
        occurrence of any known game directory in the path and return from there.

        Args:
            file_path: Full path to the file

        Returns:
            Data-relative path (e.g., 'meshes/armor/file.nif')
        """
        # Normalize path separators
        norm_path = file_path.replace('\\', '/')
        path_parts = norm_path.split('/')

        # Get real game directories (bulletproof approach!)
        if self.game_directories:
            known_dirs = self.game_directories['combined']
        else:
            # Use game scanner fallback if no game path provided
            known_dirs = self.game_scanner.fallback_directories.get(self.game_type, set())

        # Step 1: Look for any known game directory in the path (case-insensitive)
        for i, part in enumerate(path_parts):
            if part.lower() in known_dirs:
                # Found a game directory! Return path from here onwards
                data_relative = '/'.join(path_parts[i:])
                log(f"Found game dir '{part}': {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # Step 2: Look for explicit "Data" directory
        for i, part in enumerate(path_parts):
            if part.lower() == 'data' and i < len(path_parts) - 1:
                # Found Data directory! Return everything after it
                data_relative = '/'.join(path_parts[i+1:])
                log(f"Found Data folder: {file_path} → {data_relative}", debug_only=True, log_type='INFO')
                return data_relative

        # Step 3: Final fallback - preserve directory structure (bulletproof approach!)
        if len(path_parts) >= 2:
            fallback_path = '/'.join(path_parts[-2:])
            log(f"Directory structure fallback: {file_path} → {fallback_path}", debug_only=True, log_type='WARNING')
            return fallback_path
        else:
            filename = os.path.basename(file_path)
            log(f"Filename only fallback: {file_path} → {filename}", debug_only=True, log_type='WARNING')
            return filename


