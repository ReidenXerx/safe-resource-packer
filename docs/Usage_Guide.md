# Usage Guide

This guide covers common usage patterns and scenarios for Safe Resource Packer.

## Installation

### From Source

```bash
git clone https://github.com/yourusername/safe-resource-packer.git
cd safe-resource-packer
pip install -e .
```

### From PyPI (when available)

```bash
pip install safe-resource-packer
```

## Command Line Usage

### Basic Syntax

```bash
safe-resource-packer --source SOURCE --generated GENERATED --output-pack PACK --output-loose LOOSE [OPTIONS]
```

### Required Arguments

-   `--source`: Path to your reference files (e.g., Skyrim Data folder)
-   `--generated`: Path to generated files (e.g., BodySlide output)
-   `--output-pack`: Directory for files safe to pack into archives
-   `--output-loose`: Directory for files that should stay loose

### Optional Arguments

-   `--threads N`: Number of processing threads (default: 8)
-   `--debug`: Enable detailed debug logging
-   `--log FILE`: Log file path (default: safe_resource_packer.log)
-   `--help`: Show help message
-   `--version`: Show version information

## Common Scenarios

### Skyrim Special Edition BodySlide

Process BodySlide generated files for Skyrim SE:

```bash
safe-resource-packer \
  --source "C:\\Games\\Skyrim Special Edition\\Data" \
  --generated "C:\\Users\\YourUser\\Documents\\My Games\\Skyrim Special Edition\\CalienteTools\\BodySlide\\ShapeData" \
  --output-pack "./skyrim_se_pack" \
  --output-loose "./skyrim_se_loose" \
  --threads 12
```

### Skyrim Legendary Edition BodySlide

```bash
safe-resource-packer \
  --source "C:\\Games\\Skyrim\\Data" \
  --generated "C:\\Users\\YourUser\\Documents\\My Games\\Skyrim\\CalienteTools\\BodySlide\\ShapeData" \
  --output-pack "./skyrim_le_pack" \
  --output-loose "./skyrim_le_loose"
```

### Fallout 4 BodySlide

```bash
safe-resource-packer \
  --source "C:\\Games\\Fallout 4\\Data" \
  --generated "C:\\Users\\YourUser\\Documents\\My Games\\Fallout 4\\F4SE\\Plugins\\BodySlide\\ShapeData" \
  --output-pack "./fo4_pack" \
  --output-loose "./fo4_loose"
```

### Fallout New Vegas

```bash
safe-resource-packer \
  --source "C:\\Games\\Fallout New Vegas\\Data" \
  --generated "C:\\Users\\YourUser\\Documents\\My Games\\FalloutNV\\BodySlide\\ShapeData" \
  --output-pack "./fnv_pack" \
  --output-loose "./fnv_loose"
```

### Generic File Processing

```bash
safe-resource-packer \
  --source "./reference_files" \
  --generated "./modified_files" \
  --output-pack "./safe_to_pack" \
  --output-loose "./must_stay_loose" \
  --debug
```

## Understanding the Output

### Console Output

During processing, you'll see:

```
[2025-01-20 15:30:45] Starting Safe Resource Packer...
[2025-01-20 15:30:45] Source: C:\Games\Skyrim Special Edition\Data
[2025-01-20 15:30:45] Generated: C:\Users\User\Documents\My Games\Skyrim Special Edition\CalienteTools\BodySlide\ShapeData
[2025-01-20 15:30:45] Output Pack: ./skyrim_pack
[2025-01-20 15:30:45] Output Loose: ./skyrim_loose
[2025-01-20 15:30:45] Threads: 8
[2025-01-20 15:30:45] Debug: False
[2025-01-20 15:30:46] Copying source to temp directory: /tmp/tmp_abc123
[2025-01-20 15:30:52] Classifying generated files by path override logic...
[========================================] 100.0% | Classifying
[2025-01-20 15:31:15]

===== SUMMARY =====
[2025-01-20 15:31:15] Classified for packing (new): 1247
[2025-01-20 15:31:15] Classified for loose (override): 89
[2025-01-20 15:31:15] Skipped (identical): 2156
[2025-01-20 15:31:15] Skipped or errored: 3
[2025-01-20 15:31:15]
[2025-01-20 15:31:15] ✅ Processing completed successfully!
[2025-01-20 15:31:15] Log written to safe_resource_packer.log
```

### Result Categories

1. **Pack files** (new): Files that don't exist in the source, safe to pack into BSA/BA2
2. **Loose files** (override): Files that differ from source, should stay as loose files
3. **Skipped** (identical): Files identical to source, no processing needed
4. **Errors**: Files that couldn't be processed (check log for details)

### Log File

The log file contains detailed information:

```
[2025-01-20 15:30:45] Starting Safe Resource Packer...
[2025-01-20 15:30:45] Source: C:\Games\Skyrim Special Edition\Data
...
[2025-01-20 15:30:52] Classifying generated files by path override logic...
[2025-01-20 15:31:15] ✅ Processing completed successfully!

[SKIPPED FILES]
[HASH FAIL] meshes/actors/character/facegendata/corrupted.nif: Permission denied
[COPY FAIL] textures/actors/character/large_texture.dds: Disk full
```

## Python API Usage

### Basic Usage

```python
from safe_resource_packer import SafeResourcePacker

# Create packer instance
packer = SafeResourcePacker(threads=8, debug=False)

# Process resources
try:
    pack_count, loose_count, skip_count = packer.process_resources(
        source_path="/path/to/skyrim/Data",
        generated_path="/path/to/bodyslide/output",
        output_pack="./pack",
        output_loose="./loose"
    )

    print(f"Files to pack: {pack_count}")
    print(f"Files to keep loose: {loose_count}")
    print(f"Files skipped: {skip_count}")

except Exception as e:
    print(f"Error: {e}")
finally:
    packer.cleanup_temp()
```

### Advanced Usage with Logging

```python
from safe_resource_packer import SafeResourcePacker
from safe_resource_packer.utils import set_debug, write_log_file, get_skipped

# Enable debug mode
set_debug(True)

# Create packer with more threads
packer = SafeResourcePacker(threads=16, debug=True)

try:
    # Process resources
    pack_count, loose_count, skip_count = packer.process_resources(
        source_path="/path/to/source",
        generated_path="/path/to/generated",
        output_pack="./pack",
        output_loose="./loose"
    )

    # Check for any skipped files
    skipped = get_skipped()
    if skipped:
        print("Some files were skipped:")
        for skip in skipped:
            print(f"  {skip}")

    # Write detailed log
    write_log_file("detailed_processing.log")

except Exception as e:
    print(f"Processing failed: {e}")
    write_log_file("error_log.log")
```

## Best Practices

### Before Processing

1. **Backup your files**: Always backup important data before processing
2. **Verify paths**: Ensure source and generated directories exist and are accessible
3. **Check disk space**: Ensure sufficient space for output directories
4. **Close other applications**: Close mod managers or games that might lock files

### During Processing

1. **Monitor progress**: Watch the progress bar and console output
2. **Don't interrupt**: Let the process complete to avoid partial results
3. **Check for errors**: Watch for permission or disk space errors

### After Processing

1. **Review the summary**: Check the counts make sense for your use case
2. **Examine the log**: Look for any errors or warnings
3. **Test the results**: Verify files are in the correct output directories
4. **Archive pack files**: Create BSA/BA2 archives from the pack directory
5. **Deploy loose files**: Copy loose files to your game's Data directory

## Troubleshooting

### Common Issues

#### Permission Errors

```
[COPY FAIL] file.txt: Permission denied
```

**Solution**: Run as administrator or check file permissions

#### Disk Space Errors

```
[COPY FAIL] large_file.dds: No space left on device
```

**Solution**: Free up disk space or use a different output location

#### Path Not Found

```
❌ Source path does not exist: /invalid/path
```

**Solution**: Verify the path exists and is accessible

#### No Files Processed

If all files are skipped, check:

-   Generated directory contains files
-   File paths are correct
-   Files aren't locked by other applications

### Debug Mode

Enable debug mode for detailed information:

```bash
safe-resource-packer --source ... --generated ... --output-pack ... --output-loose ... --debug
```

Debug mode shows:

-   Individual file processing decisions
-   Hash calculations
-   Path matching results
-   Detailed error information

### Performance Issues

If processing is slow:

1. **Increase threads**: Use more threads if you have multiple CPU cores
2. **Use SSD storage**: Fast storage improves file I/O
3. **Close other applications**: Free up system resources
4. **Process smaller batches**: Split large file sets into smaller batches

### Memory Issues

If you run out of memory:

-   The tool is designed to use minimal memory
-   Check for other applications using memory
-   Consider processing files in smaller batches

## Integration with Mod Managers

### Mod Organizer 2

1. Process files using Safe Resource Packer
2. Create BSA from pack directory using tools like BSArch
3. Install the BSA as a mod in MO2
4. Copy loose files to appropriate mod directories

### Vortex

1. Process files using Safe Resource Packer
2. Create archive from pack directory
3. Install archive through Vortex
4. Manually place loose files in staging folder

### Manual Installation

1. Process files using Safe Resource Packer
2. Create BSA/BA2 from pack directory
3. Place BSA/BA2 in game's Data directory
4. Copy loose files directly to Data directory

## Automation Scripts

### Batch Processing Script

```bash
#!/bin/bash
# Process multiple BodySlide outputs

SKYRIM_DATA="/path/to/skyrim/Data"
BODYSLIDE_ROOT="/path/to/bodyslide"

# Process different body types
for body in CBBE UNP 3BBB; do
    echo "Processing $body..."
    safe-resource-packer \
        --source "$SKYRIM_DATA" \
        --generated "$BODYSLIDE_ROOT/$body/ShapeData" \
        --output-pack "./output/${body}_pack" \
        --output-loose "./output/${body}_loose" \
        --log "${body}_processing.log"
done
```

### Python Automation

```python
import os
from safe_resource_packer import SafeResourcePacker

# Configuration for multiple body types
configs = [
    {"name": "CBBE", "path": "/path/to/cbbe/output"},
    {"name": "UNP", "path": "/path/to/unp/output"},
    {"name": "3BBB", "path": "/path/to/3bbb/output"}
]

source_path = "/path/to/skyrim/Data"
packer = SafeResourcePacker(threads=12)

for config in configs:
    print(f"Processing {config['name']}...")

    try:
        pack_count, loose_count, skip_count = packer.process_resources(
            source_path=source_path,
            generated_path=config["path"],
            output_pack=f"./output/{config['name']}_pack",
            output_loose=f"./output/{config['name']}_loose"
        )

        print(f"  Pack: {pack_count}, Loose: {loose_count}, Skip: {skip_count}")

    except Exception as e:
        print(f"  Error processing {config['name']}: {e}")
```
