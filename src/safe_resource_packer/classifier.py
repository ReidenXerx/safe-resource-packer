"""
File classification logic for Safe Resource Packer.
"""

import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .dynamic_progress import log, print_progress, log_classification_progress
from .utils import file_hash, validate_path_length, sanitize_filename, check_disk_space, format_bytes, safe_walk, is_file_locked, wait_for_file_unlock
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
        Copy file to destination with error handling and proper game directory structure.

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
            
            # Validate path length before attempting operation
            is_valid, error_msg = validate_path_length(dest_path)
            if not is_valid:
                with self.lock:
                    self.skipped.append(f"[PATH TOO LONG] {rel_path}: {error_msg}")
                log(f"[PATH TOO LONG] {rel_path}: {error_msg}", debug_only=True, log_type='COPY FAIL')
                return False
            
            # Check if we have enough disk space before copying
            try:
                file_size = os.path.getsize(src)
                has_space, available, required = check_disk_space(base_out, file_size)
                if not has_space:
                    with self.lock:
                        self.skipped.append(f"[DISK FULL] {rel_path}: Need {format_bytes(required)}, have {format_bytes(available)}")
                    log(f"[DISK FULL] {rel_path}: Need {format_bytes(required)}, have {format_bytes(available)}", 
                        debug_only=True, log_type='COPY FAIL')
                    return False
            except OSError:
                # If we can't check file size, proceed anyway
                pass
            
            # Create destination directory with error handling
            dest_dir = os.path.dirname(dest_path)
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except OSError as e:
                if e.errno == 36:  # File name too long
                    # Try with sanitized filename
                    sanitized_name = sanitize_filename(os.path.basename(dest_path))
                    dest_path = os.path.join(dest_dir, sanitized_name)
                    log(f"[FILENAME SANITIZED] {rel_path} → {sanitized_name}", debug_only=True, log_type='INFO')
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                else:
                    raise
            
            # Skip proactive locking checks - let the copy operation handle it naturally
            
            # Perform the copy with retry logic for transient failures
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.copy2(src, dest_path)
                    log(f"Copied with Data structure: {src} → {data_rel_path}", debug_only=True, log_type='INFO')
                    return True
                except (OSError, IOError) as e:
                    if attempt < max_retries - 1:
                        # For permission errors, try waiting a bit
                        if "Permission denied" in str(e) or "being used by another process" in str(e):
                            log(f"[COPY RETRY] {rel_path}: File may be locked, waiting...", 
                                debug_only=True, log_type='WARNING')
                            import time
                            time.sleep(1)  # Wait 1 second before retry
                        else:
                            log(f"[COPY RETRY] {rel_path}: Attempt {attempt + 1} failed, retrying...", 
                                debug_only=True, log_type='WARNING')
                        continue
                    else:
                        raise
            
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
                    else:
                        # Copy failed, but still count as loose since file differs
                        log(f"[LOOSE FAIL] {rel_path} copy failed but differs from source", debug_only=True, log_type='LOOSE FAIL')
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
        # Thread-safe reset of skipped list for this classification run
        with self.lock:
            self.skipped = []

        # Create temporary directories for this classification session
        import tempfile
        import uuid
        
        # Create unique temp directories for this session
        session_id = str(uuid.uuid4())[:8]
        temp_pack_dir = os.path.join(tempfile.gettempdir(), f"srp_pack_{session_id}")
        temp_loose_dir = os.path.join(tempfile.gettempdir(), f"srp_loose_{session_id}")
        
        # Clean and create temp directories
        if os.path.exists(temp_pack_dir):
            shutil.rmtree(temp_pack_dir)
        if os.path.exists(temp_loose_dir):
            shutil.rmtree(temp_loose_dir)
        
        os.makedirs(temp_pack_dir, exist_ok=True)
        os.makedirs(temp_loose_dir, exist_ok=True)
        
        log(f"📁 Created temp pack directory: {temp_pack_dir}", log_type='INFO')
        log(f"📁 Created temp loose directory: {temp_loose_dir}", log_type='INFO')

        all_gen_files = []
        # Use safe_walk to handle symlinks and circular references
        for root, _, files in safe_walk(generated_root, followlinks=False):
            for file in files:
                full_path = os.path.join(root, file)
                
                # Only check basic file existence, skip aggressive locking checks
                # that can cause freezing on large file sets
                if not os.path.isfile(full_path):
                    continue
                
                rel_path = os.path.relpath(full_path, generated_root)
                all_gen_files.append((full_path, rel_path))

        total = len(all_gen_files)
        current = 0
        pack_count, loose_count, skip_count = 0, 0, 0

        # Debug table functionality removed - using dynamic progress instead

        # Choose the best progress system (avoid conflicts)
        dynamic_progress_active = False
        try:
            from .dynamic_progress import start_dynamic_progress, is_dynamic_progress_enabled
            # Only use dynamic progress if no other Rich-based progress callback is active
            if is_dynamic_progress_enabled() and not hasattr(progress_callback, 'start_processing'):
                start_dynamic_progress("Classification", total)
                dynamic_progress_active = True
        except ImportError:
            pass

        # Initialize progress callback if it's a CleanOutputManager (and dynamic progress is not active)
        if hasattr(progress_callback, 'start_processing') and not dynamic_progress_active:
            progress_callback.start_processing(total)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(self.process_file, source_root, temp_pack_dir, temp_loose_dir, gp, rp)
                for gp, rp in all_gen_files
            ]
            for future in as_completed(futures):
                result, path = future.result()
                current += 1

                # Update counters FIRST
                if result == 'loose':
                    loose_count += 1
                elif result == 'pack':
                    pack_count += 1
                elif result == 'skip':
                    skip_count += 1

                # Update progress with the active progress system
                if dynamic_progress_active:
                    # Manually update dynamic progress with correct count and current file
                    try:
                        from .dynamic_progress import set_dynamic_progress_current, update_dynamic_progress_with_counts
                        set_dynamic_progress_current(current)
                        # Pass the actual accumulated file counts instead of individual results
                        
                        update_dynamic_progress_with_counts(
                            path, result, "", 
                            match_found=0,           # Not tracking matches during classification
                            no_match=pack_count,     # Files that will be packed (New Files)
                            skip=skip_count,         # Files being skipped (Identical)
                            override=loose_count,    # Files that will be loose (Overrides)
                            errors=0                 # No error tracking here
                        )
                    except ImportError:
                        pass
                elif hasattr(progress_callback, 'update_progress'):
                    progress_callback.update_progress(path, result)
                elif progress_callback:
                    progress_callback(current, total, "Classifying", path)
                else:
                    # Show beautiful progress every 10 files or on important milestones
                    if current % 10 == 0 or current == total or current <= 5:
                        log_classification_progress(current, total, path)
                    print_progress(current, total, "Classifying", path)

        # Finish the active progress system
        if dynamic_progress_active:
            try:
                from .dynamic_progress import finish_dynamic_progress
                finish_dynamic_progress()
            except ImportError:
                pass
        elif hasattr(progress_callback, 'finish_processing'):
            progress_callback.finish_processing()
        
        # Copy files from temp directories to final output directories
        try:
            # Clean final output directories
            if os.path.exists(out_pack):
                shutil.rmtree(out_pack)
            if os.path.exists(out_loose):
                shutil.rmtree(out_loose)
            
            # Create final output directories
            os.makedirs(out_pack, exist_ok=True)
            os.makedirs(out_loose, exist_ok=True)
            
            # Copy pack files
            if pack_count > 0 and os.path.exists(temp_pack_dir):
                copied_count = 0
                for root, dirs, files in os.walk(temp_pack_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_pack_dir)
                        dst_path = os.path.join(out_pack, rel_path)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        copied_count += 1
                        log(f"📦 Copied: {src_path} → {dst_path}", debug_only=True, log_type='INFO')
                log(f"📦 Copied {copied_count} files to pack directory: {out_pack}", log_type='INFO')
            
            # Copy loose files
            if loose_count > 0 and os.path.exists(temp_loose_dir):
                copied_count = 0
                for root, dirs, files in os.walk(temp_loose_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_loose_dir)
                        dst_path = os.path.join(out_loose, rel_path)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        copied_count += 1
                        log(f"📁 Copied: {src_path} → {dst_path}", debug_only=True, log_type='INFO')
                log(f"📁 Copied {copied_count} files to loose directory: {out_loose}", log_type='INFO')
            
            # Clean up temp directories
            shutil.rmtree(temp_pack_dir, ignore_errors=True)
            shutil.rmtree(temp_loose_dir, ignore_errors=True)
            log(f"🧹 Cleaned up temp directories", log_type='INFO')
            
        except Exception as e:
            log(f"⚠️ Error copying files to output directories: {e}", log_type='WARNING')
            # Still return the counts even if copying failed
        
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
            known_dirs = self.game_scanner.fallback_directories

        # Step 1: Look for any known game directory in the path (case-insensitive)
        for i, part in enumerate(path_parts):
            if part.lower() in known_dirs:
                # Found a game directory! Return path from here onwards
                data_relative = '/'.join(path_parts[i:])
                log(f"Found game dir '{part}': {file_path} → {data_relative}", debug_only=True, log_type='PATH_EXTRACT')
                return data_relative

        # Step 2: Look for explicit "Data" directory
        for i, part in enumerate(path_parts):
            if part.lower() == 'data' and i < len(path_parts) - 1:
                # Found Data directory! Return everything after it
                data_relative = '/'.join(path_parts[i+1:])
                log(f"Found Data folder: {file_path} → {data_relative}", debug_only=True, log_type='PATH_EXTRACT')
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


