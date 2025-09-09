"""
Core functionality for Safe Resource Packer.
"""

import os
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .classifier import PathClassifier
from .dynamic_progress import log, print_progress
from .utils import safe_walk

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class SafeResourcePacker:
    """Main class for safe resource packing operations."""

    def __init__(self, threads=8, debug=False, game_path=None, game_type="skyrim"):
        """
        Initialize SafeResourcePacker.

        Args:
            threads (int): Number of threads to use for processing
            debug (bool): Enable debug logging
            game_path (str): Path to game installation for directory scanning
            game_type (str): Type of game ("skyrim" or "fallout4")
        """
        self.threads = threads
        self.debug = debug
        self.game_path = game_path
        self.game_type = game_type
        self.classifier = PathClassifier(debug=debug, game_path=game_path, game_type=game_type)
        self.temp_dir = None

    def copy_folder_to_temp(self, source, generated_path=None):
        """
        Intelligently copy only relevant source directories to temporary directory.

        This is a HUGE optimization - instead of copying the entire game Data folder
        (50-100GB+), we only copy directories that exist in the mod folder.

        Args:
            source (str): Path to source directory
            generated_path (str): Path to generated files (to analyze what directories we need)

        Returns:
            tuple: (temp_source_path, temp_directory)
        """
        self.temp_dir = tempfile.mkdtemp()
        dest_path = os.path.join(self.temp_dir, 'source')

        if generated_path:
            log(f"🧠 Smart selective copying: analyzing mod directories...", log_type='INFO')
            return self._selective_copy_with_analysis(source, dest_path, generated_path)
        else:
            log(f"📁 Full copy mode (no generated path provided)", log_type='INFO')
            return self._full_copy(source, dest_path)

    def _selective_copy_with_analysis(self, source, dest_path, generated_path):
        """
        Analyze mod directories and copy only relevant source directories.

        Args:
            source (str): Source directory path
            dest_path (str): Destination path for selective copy
            generated_path (str): Generated files path to analyze

        Returns:
            tuple: (dest_path, temp_dir)
        """
        # Step 1: Analyze what directories the mod actually uses
        mod_directories = self._analyze_mod_directories(generated_path)
        log(f"📊 Mod uses {len(mod_directories)} directories: {sorted(list(mod_directories))}", log_type='INFO')

        # Step 2: Get comprehensive directory analysis with proper case handling
        analysis_info = self._get_directory_analysis_info(source, mod_directories)
        source_directories = analysis_info['source_directories']

        # Log case-insensitive matching results
        if analysis_info['mod_only_normalized']:
            log(f"🆕 Mod-only directories: {sorted(list(analysis_info['mod_only_normalized']))}", log_type='INFO')
        else:
            log(f"✅ All mod directories exist in source (case-insensitive)", log_type='INFO')

        # Step 3: Calculate space savings
        total_source_size = self._estimate_directory_size(source)
        selective_size = sum(self._estimate_directory_size(os.path.join(source, d))
                           for d in source_directories if os.path.exists(os.path.join(source, d)))

        if total_source_size > 0:
            savings_percent = ((total_source_size - selective_size) / total_source_size) * 100
            log(f"💾 Space optimization: {savings_percent:.1f}% reduction ({self._format_size(total_source_size - selective_size)} saved)",
                log_type='SUCCESS')

        # Step 4: Perform selective copy
        os.makedirs(dest_path, exist_ok=True)

        copied_dirs = []
        total_files = 0

        # Count files for progress
        for dir_name in source_directories:
            source_dir = os.path.join(source, dir_name)
            if os.path.exists(source_dir):
                dir_files = sum(len(files) for _, _, files in os.walk(source_dir))
                total_files += dir_files

        log(f"📁 Selective copy: {len(source_directories)} directories, {total_files} files", log_type='INFO')

        # Copy with progress
        if RICH_AVAILABLE and total_files > 50:
            self._selective_copy_with_progress(source, dest_path, source_directories, total_files)
        else:
            self._selective_copy_simple(source, dest_path, source_directories, total_files)

        # Step 5: Handle mod-only directories (edge case)
        mod_only_dirs = mod_directories - set(source_directories)
        if mod_only_dirs:
            log(f"🆕 Mod has {len(mod_only_dirs)} new directories not in source: {sorted(list(mod_only_dirs))}",
                log_type='INFO')
            # These will be treated as completely new files during classification

        return dest_path, self.temp_dir

    def _analyze_mod_directories(self, generated_path):
        """
        Analyze what top-level directories the mod actually uses.

        Args:
            generated_path (str): Path to generated files

        Returns:
            set: Set of normalized directory names used by the mod (lowercase)
        """
        mod_directories = set()

        # Walk through mod files and extract top-level directories (safely)
        for root, dirs, files in safe_walk(generated_path, followlinks=False):
            if files:  # Only count directories that actually contain files
                rel_path = os.path.relpath(root, generated_path)
                if rel_path != '.':  # Not the root itself
                    # Get the top-level directory and normalize to lowercase
                    top_dir = rel_path.split(os.sep)[0]
                    mod_directories.add(top_dir.lower())
                else:
                    # Files directly in root - add all immediate subdirectories
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        if any(os.path.isfile(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))):
                            mod_directories.add(dir_name.lower())

        return mod_directories

    def _find_source_directories(self, source, mod_directories):
        """
        Find which mod directories exist in the source.

        Args:
            source (str): Source directory path
            mod_directories (set): Normalized directory names used by mod (lowercase)

        Returns:
            list: List of actual directory names that exist in source
        """
        source_directories = []

        for mod_dir in mod_directories:
            # Check case-insensitive (game directories can have different cases)
            source_dir = self._find_directory_case_insensitive(source, mod_dir)
            if source_dir:
                source_directories.append(source_dir)
                log(f"✅ Found source directory: {mod_dir} → {source_dir}", debug_only=True, log_type='INFO')
            else:
                log(f"🆕 Mod-only directory: {mod_dir} (not in source)", debug_only=True, log_type='INFO')

        return source_directories

    def _get_directory_analysis_info(self, source, mod_directories):
        """
        Get comprehensive directory analysis information with proper case handling.

        Args:
            source (str): Source directory path
            mod_directories (set): Normalized directory names used by mod (lowercase)

        Returns:
            dict: Dictionary with analysis information including normalized and actual names
        """
        source_directories = []
        source_normalized = set()
        mod_only_normalized = set()

        for mod_dir in mod_directories:
            # Check case-insensitive (game directories can have different cases)
            source_dir = self._find_directory_case_insensitive(source, mod_dir)
            if source_dir:
                source_directories.append(source_dir)
                source_normalized.add(mod_dir)  # mod_dir is already normalized
                log(f"✅ Found source directory: {mod_dir} → {source_dir}", debug_only=True, log_type='INFO')
            else:
                mod_only_normalized.add(mod_dir)
                log(f"🆕 Mod-only directory: {mod_dir} (not in source)", debug_only=True, log_type='INFO')

        return {
            'mod_directories': mod_directories,  # normalized names
            'source_directories': source_directories,  # actual names from source
            'source_normalized': source_normalized,  # normalized names that exist in source
            'mod_only_normalized': mod_only_normalized  # normalized names that don't exist in source
        }

    def _find_directory_case_insensitive(self, parent_dir, target_dir):
        """
        Find directory with case-insensitive matching.

        Args:
            parent_dir (str): Parent directory to search in
            target_dir (str): Directory name to find

        Returns:
            str or None: Actual directory name if found
        """
        try:
            for item in os.listdir(parent_dir):
                item_path = os.path.join(parent_dir, item)
                if os.path.isdir(item_path) and item.lower() == target_dir.lower():
                    return item
        except (OSError, FileNotFoundError):
            pass
        return None

    def _estimate_directory_size(self, directory):
        """
        Estimate directory size (quick approximation).

        Args:
            directory (str): Directory path

        Returns:
            int: Estimated size in bytes
        """
        try:
            if not os.path.exists(directory):
                return 0

            total_size = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        pass
            return total_size
        except:
            return 0

    def _format_size(self, size_bytes):
        """
        Format size in human-readable format.

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"

    def _selective_copy_with_progress(self, source, dest_path, source_directories, total_files):
        """Copy directories with Rich progress bar."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ) as progress:

                task = progress.add_task("Copying directories...", total=total_files)
                copied_files = 0

                for dir_name in source_directories:
                    source_dir = os.path.join(source, dir_name)
                    dest_dir = os.path.join(dest_path, dir_name)

                    if os.path.exists(source_dir):
                        progress.update(task, description=f"Copying {dir_name}/...")

                        for root, dirs, files in os.walk(source_dir):
                            # Create directory structure
                            rel_root = os.path.relpath(root, source_dir)
                            if rel_root == '.':
                                current_dest = dest_dir
                            else:
                                current_dest = os.path.join(dest_dir, rel_root)
                            os.makedirs(current_dest, exist_ok=True)

                            # Copy files
                            for file in files:
                                src_file = os.path.join(root, file)
                                dst_file = os.path.join(current_dest, file)
                                try:
                                    shutil.copy2(src_file, dst_file)
                                    copied_files += 1
                                    progress.update(task, advance=1)
                                except Exception as e:
                                    log(f"Failed to copy {src_file}: {e}", debug_only=True, log_type='WARNING')

                progress.update(task, description=f"Completed! Copied {len(source_directories)} directories")
        except Exception as e:
            log(f"Progress copy failed, falling back to simple copy: {e}", log_type='WARNING')
            self._selective_copy_simple(source, dest_path, source_directories, total_files)

    def _selective_copy_simple(self, source, dest_path, source_directories, total_files):
        """Copy directories with simple progress."""
        if total_files > 50:
            print(f"📁 Copying {len(source_directories)} directories ({total_files} files)...")

        for i, dir_name in enumerate(source_directories):
            source_dir = os.path.join(source, dir_name)
            dest_dir = os.path.join(dest_path, dir_name)

            if os.path.exists(source_dir):
                if total_files > 50:
                    print(f"  [{i+1}/{len(source_directories)}] {dir_name}/")

                try:
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                except Exception as e:
                    log(f"Failed to copy directory {dir_name}: {e}", log_type='WARNING')

    def _full_copy(self, source, dest_path):
        """Fallback to full copy when no generated path provided."""
        # Count total files for progress
        total_files = sum(len(files) for _, _, files in os.walk(source))

        if RICH_AVAILABLE and total_files > 100:  # Show progress for large folders
            self._copy_with_progress(source, dest_path, total_files)
        else:
            # Simple copy for small folders or when Rich not available
            if total_files > 100:
                print(f"📁 Copying {total_files} files to temporary directory...")
            shutil.copytree(source, dest_path, dirs_exist_ok=True)

        return dest_path, self.temp_dir

    def process_resources(self, source_path, generated_path, output_pack, output_loose, progress_callback=None):
        """
        Process resources and classify them for packing or loose deployment.

        Args:
            source_path (str): Path to source/reference files
            generated_path (str): Path to generated/modified files
            output_pack (str): Path for files safe to pack
            output_loose (str): Path for files that should remain loose
            progress_callback (callable): Optional callback for progress updates

        Returns:
            tuple: (pack_count, loose_count, skip_count)
        """
        # Create smart selective copy of source for safe processing
        real_source, temp_dir = self.copy_folder_to_temp(source_path, generated_path)

        try:
            log("Classifying generated files by path override logic...", log_type='INFO')
            return self.classifier.classify_by_path(
                real_source, generated_path, output_pack, output_loose, self.threads, progress_callback
            )
        finally:
            self.cleanup_temp()

    def cleanup_temp(self):
        """Clean up temporary directories."""
        if self.temp_dir:
            try:
                # Count files for progress if it's a large directory
                total_files = 0
                try:
                    total_files = sum(len(files) for _, _, files in os.walk(self.temp_dir))
                except:
                    pass

                if RICH_AVAILABLE and total_files > 100:
                    self._cleanup_with_progress(self.temp_dir, total_files)
                else:
                    if total_files > 100:
                        print(f"🧹 Cleaning up {total_files} temporary files...")
                    shutil.rmtree(self.temp_dir)

                log(f"Cleaned up temp directory: {self.temp_dir}", log_type='SUCCESS')
            except Exception as e:
                log(f"Failed to clean temp directory: {e}", log_type='ERROR')
            finally:
                self.temp_dir = None

    def _copy_with_progress(self, source, dest, total_files):
        """Copy files with Rich progress bar."""
        console = Console()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("📁 Copying source files...", total=total_files)

            def copy_with_callback(src, dst, *, follow_symlinks=True):
                """Copy function that updates progress."""
                for root, dirs, files in os.walk(src):
                    # Create destination directories
                    rel_root = os.path.relpath(root, src)
                    dest_root = os.path.join(dst, rel_root) if rel_root != '.' else dst
                    os.makedirs(dest_root, exist_ok=True)

                    # Copy files
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dest_root, file)
                        try:
                            shutil.copy2(src_file, dst_file)
                            progress.update(task, advance=1)
                        except Exception as e:
                            log(f"Failed to copy {src_file}: {e}", log_type='WARNING')
                            progress.update(task, advance=1)

            copy_with_callback(source, dest)

    def _cleanup_with_progress(self, temp_dir, total_files):
        """Clean up files with Rich progress bar."""
        console = Console()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("🧹 Cleaning temporary files...", total=total_files)

            def remove_with_progress(path):
                """Remove files and update progress."""
                if os.path.isfile(path):
                    try:
                        os.remove(path)
                        progress.update(task, advance=1)
                    except:
                        progress.update(task, advance=1)
                elif os.path.isdir(path):
                    try:
                        for root, dirs, files in os.walk(path, topdown=False):
                            # Remove files
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    os.remove(file_path)
                                    progress.update(task, advance=1)
                                except:
                                    progress.update(task, advance=1)
                            # Remove empty directories
                            for dir in dirs:
                                dir_path = os.path.join(root, dir)
                                try:
                                    os.rmdir(dir_path)
                                except:
                                    pass
                        # Remove the root directory
                        os.rmdir(path)
                    except Exception as e:
                        log(f"Error during cleanup: {e}", log_type='WARNING')

            remove_with_progress(temp_dir)
