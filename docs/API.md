# API Documentation

This document provides detailed information about the Safe Resource Packer API.

## 🏗️ **Architecture Overview**

Safe Resource Packer provides two main functionalities with clear function naming:

### **Quick Start Mode** (Single Mod Processing)
- **Prefix**: `quick_start_` or `single_mod_`
- **Purpose**: Process individual mods with interactive wizards
- **Entry Points**: Console UI, Enhanced CLI

### **Batch Repacking Mode** (Multiple Mods Processing)
- **Prefix**: `batch_repack_` or `batch_mod_`
- **Purpose**: Process collections of mods automatically
- **Entry Points**: Batch Mod Repacker

## Core Classes

### SafeResourcePacker

The main class for resource packing operations.

```python
from safe_resource_packer import SafeResourcePacker

packer = SafeResourcePacker(threads=8, debug=False)
```

#### Constructor Parameters

-   `threads` (int, optional): Number of threads to use for processing. Default: 8
-   `debug` (bool, optional): Enable debug logging. Default: False

#### Methods

##### `process_single_mod_resources(source_path, generated_path, output_pack, output_loose, output_blacklisted)`

Process single mod resources and classify them for packing or loose deployment.

**Parameters:**

-   `source_path` (str): Path to source/reference files
-   `generated_path` (str): Path to generated/modified files
-   `output_pack` (str): Path for files safe to pack
-   `output_loose` (str): Path for files that should remain loose
-   `output_blacklisted` (str): Path for blacklisted files
-   `progress_callback` (callable, optional): Optional callback for progress updates

**Returns:**

-   `tuple`: (pack_count, loose_count, blacklisted_count, skip_count)

**Example:**

```python
pack_count, loose_count, blacklisted_count, skip_count = packer.process_single_mod_resources(
    source_path="/path/to/skyrim/Data",
    generated_path="/path/to/bodyslide/output",
    output_pack="./pack",
    output_loose="./loose",
    output_blacklisted="./blacklisted"
)
```

##### `cleanup_temp()`

Clean up temporary directories created during processing.

```python
packer.cleanup_temp()
```

### PathClassifier

Handles file classification based on path matching and hash comparison.

```python
from safe_resource_packer.classifier import PathClassifier

classifier = PathClassifier(debug=False)
```

#### Constructor Parameters

-   `debug` (bool, optional): Enable debug logging. Default: False

#### Methods

##### `classify_by_path(source_root, generated_root, out_pack, out_loose, threads=8)`

Classify all files in generated directory.

**Parameters:**

-   `source_root` (str): Root directory of source files
-   `generated_root` (str): Root directory of generated files
-   `out_pack` (str): Output directory for packable files
-   `out_loose` (str): Output directory for loose files
-   `threads` (int, optional): Number of threads to use. Default: 8

**Returns:**

-   `tuple`: (pack_count, loose_count, skip_count)

##### `find_file_case_insensitive(root, rel_path)`

Find file with case-insensitive matching.

**Parameters:**

-   `root` (str): Root directory to search in
-   `rel_path` (str): Relative path to find

**Returns:**

-   `str` or `None`: Full path to found file, or None if not found

##### `get_skipped_files()`

Get list of skipped files.

**Returns:**

-   `list`: List of skipped file messages

### BatchModRepacker

Handles batch processing of multiple mods.

```python
from safe_resource_packer.batch_repacker import BatchModRepacker

repacker = BatchModRepacker(game_type="skyrim", threads=8)
```

#### Constructor Parameters

-   `game_type` (str, optional): Target game type. Default: "skyrim"
-   `threads` (int, optional): Number of threads to use. Default: 8

#### Methods

##### `process_mods(collection_path, output_path, selected_mods=None)`

Process multiple mods in batch.

**Parameters:**

-   `collection_path` (str): Path to mod collection directory
-   `output_path` (str): Base output directory for processed mods
-   `selected_mods` (list, optional): List of mod indices to process. If None, processes all mods

**Returns:**

-   `dict`: Processing results with success/failure counts

##### `_batch_repack_process_single_mod(mod_info, output_path)`

Process a single mod during batch repacking.

**Parameters:**

-   `mod_info` (ModInfo): Mod information object
-   `output_path` (str): Output directory for this mod

**Returns:**

-   `tuple`: (success: bool, result_path_or_error_message: str)

## Utility Functions

### Logging Functions

```python
from safe_resource_packer.utils import log, set_debug, write_log_file

# Enable debug mode
set_debug(True)

# Log a message
log("Processing started")

# Log debug-only message
log("Debug info", debug_only=True)

# Write logs to file
write_log_file("processing.log")
```

#### `log(message, debug_only=False)`

Log a message with timestamp.

**Parameters:**

-   `message` (str): Message to log
-   `debug_only` (bool, optional): Only log if debug mode is enabled. Default: False

#### `set_debug(debug_mode)`

Set global debug mode.

**Parameters:**

-   `debug_mode` (bool): Enable or disable debug mode

#### `write_log_file(path)`

Write all logs to a file.

**Parameters:**

-   `path` (str): Path to log file

### File Functions

```python
from safe_resource_packer.utils import file_hash, print_progress

# Calculate file hash
hash_value = file_hash("/path/to/file.txt")

# Display progress
print_progress(50, 100, "Processing", "file.txt")
```

#### `file_hash(path)`

Calculate SHA1 hash of a file.

**Parameters:**

-   `path` (str): Path to file

**Returns:**

-   `str` or `None`: SHA1 hash or None if error

#### `print_progress(current, total, stage, extra="")`

Print a progress bar.

**Parameters:**

-   `current` (int): Current progress
-   `total` (int): Total items
-   `stage` (str): Current stage description
-   `extra` (str, optional): Extra information to display

### Log Management

```python
from safe_resource_packer.utils import get_logs, get_skipped, clear_logs

# Get all logs
logs = get_logs()

# Get skipped files
skipped = get_skipped()

# Clear all logs
clear_logs()
```

#### `get_logs()`

Get copy of all logs.

**Returns:**

-   `list`: List of log messages

#### `get_skipped()`

Get copy of all skipped files.

**Returns:**

-   `list`: List of skipped file messages

#### `clear_logs()`

Clear all logs and skipped files.

## Command Line Interface

The CLI is available through the `safe_resource_packer.cli` module:

```python
from safe_resource_packer.cli import main

# This is equivalent to running the command line tool
main()
```

## Error Handling

The API uses standard Python exceptions. Common exceptions you might encounter:

-   `FileNotFoundError`: Source or generated directories don't exist
-   `PermissionError`: Insufficient permissions to read/write files
-   `OSError`: General file system errors

Example error handling:

```python
try:
    pack_count, loose_count, skip_count = packer.process_resources(
        source_path=source,
        generated_path=generated,
        output_pack=pack_dir,
        output_loose=loose_dir
    )
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
except PermissionError as e:
    print(f"Permission denied: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Threading Considerations

The API is thread-safe for concurrent processing of different file sets, but:

-   Don't process the same files simultaneously with multiple instances
-   The logging system uses thread-safe operations
-   File I/O operations are protected with locks where necessary

## Performance Tips

1. **Adjust thread count**: Set `threads` based on your CPU cores and I/O capacity
2. **Use SSDs**: File hashing and copying benefit from fast storage
3. **Enable debug sparingly**: Debug mode generates more output and can slow processing
4. **Process in batches**: For very large file sets, consider processing in smaller batches

## Memory Usage

The API is designed to be memory-efficient:

-   Files are processed individually, not loaded entirely into memory
-   Temporary directories are cleaned up automatically
-   Hash calculations stream file contents rather than loading them entirely

## Examples

See the `examples/` directory for comprehensive usage examples:

-   `basic_usage.py`: Simple API usage
-   `skyrim_bodyslide_example.py`: Game-specific processing
-   `config_example.py`: Configuration-driven processing
