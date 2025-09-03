"""
Core functionality for Safe Resource Packer.
"""

import os
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .classifier import PathClassifier
from .utils import log, print_progress

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


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
        dest_path = os.path.join(self.temp_dir, 'source')

        log(f"Copying source to temp directory: {self.temp_dir}", log_type='INFO')

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
        # Create temporary copy of source for safe processing
        real_source, temp_dir = self.copy_folder_to_temp(source_path)

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
