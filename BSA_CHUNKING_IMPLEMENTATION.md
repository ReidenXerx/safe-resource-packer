# BSA Chunking Implementation - CAO Style

## Overview

Safe Resource Packer now supports CAO (Cathedral Assets Optimizer) style BSA chunking to prevent PGPatcher and other tools from encountering errors when processing large archives. This implementation splits large BSA archives into chunks of maximum 2GB each, following the same naming convention as CAO.

## Problem Solved

Previously, when Safe Resource Packer created large BSA archives (>2GB), tools like PGPatcher would throw errors because they couldn't handle the large file size. CAO solved this by splitting archives into chunks, and now Safe Resource Packer does the same.

## Implementation Details

### 1. BSArch Service Enhancement (`bsarch_service.py`)

**New Method: `execute_bsarch_chunked()`**
- Automatically detects when total file size exceeds 2GB limit
- Creates multiple chunked archives instead of single large archive
- Uses intelligent file distribution algorithm (bin packing)
- Maintains proper game directory structure in each chunk

**Chunk Naming Convention (CAO Style):**
- `pack.bsa` - First chunk
- `pack0.bsa` - Second chunk  
- `pack1.bsa` - Third chunk
- `pack2.bsa` - Fourth chunk
- etc.

**Key Features:**
- **Size Limit**: 2GB maximum per chunk (configurable)
- **File Distribution**: Optimized bin packing algorithm
- **Integrity Checking**: Verifies no files are lost during chunking
- **Structure Preservation**: Maintains proper game directory structure
- **Error Handling**: Comprehensive error handling and cleanup

### 2. ESP Manager Enhancement (`esp_manager.py`)

**Updated `create_esp()` method:**
- Now accepts multiple BSA files (chunks)
- Provides detailed logging for chunked archives
- Detects CAO-style naming patterns
- Validates all BSA files exist before ESP creation

### 3. Package Builder Integration (`package_builder.py`)

**Updated `_create_packed_archive()` method:**
- Uses chunked BSArch creation by default
- Handles multiple BSA chunks in final package
- Updated metadata to include chunk information
- Proper cleanup of temporary files

### 4. Archive Creator Enhancement (`archive_creator.py`)

**Updated `_create_with_bsarch()` method:**
- Now uses chunked BSArch creation automatically
- Maintains backward compatibility for single archives
- Provides detailed logging for chunked archives
- Handles both single and multiple archive scenarios

### 5. Batch Repacker Integration (`batch_repacker.py`)

**Updated `_process_single_mod()` method:**
- Automatically detects and handles multiple BSA chunks
- Copies all archive chunks to final package
- Provides detailed logging for chunked archives
- Maintains compatibility with existing batch workflows

## Usage

The chunking is now automatic and transparent to users:

```python
# This will automatically create chunks if needed
success, message, created_archives = execute_bsarch_chunked_universal(
    source_dir=staging_dir,
    output_base_path=bsa_base_path,
    files=pack_files,
    game_type="skyrim",
    max_chunk_size_gb=2.0,  # CAO-style 2GB limit
    interactive=False
)
```

## File Distribution Algorithm

The implementation uses an intelligent bin packing algorithm:

1. **Sort by Size**: Files are sorted by size (largest first)
2. **Chunk Creation**: Files are distributed into chunks while respecting size limits
3. **Overflow Handling**: Files larger than 2GB get their own chunk
4. **Structure Preservation**: Directory structure is maintained in each chunk

## Integrity Verification

The system includes multiple integrity checks:

1. **File Count Verification**: Ensures all input files are processed
2. **Archive Size Validation**: Verifies archives are created successfully
3. **Existence Checks**: Confirms all chunk files exist
4. **Size Consistency**: Validates total size matches expectations

## Benefits

1. **PGPatcher Compatibility**: No more errors with large archives
2. **CAO Compatibility**: Uses same naming convention as CAO
3. **Automatic**: No user intervention required
4. **Efficient**: Optimized file distribution algorithm
5. **Reliable**: Comprehensive error handling and verification
6. **Transparent**: Works seamlessly with existing workflow
7. **Proper Game Archives**: Only creates valid BSA/BA2 files (no invalid ZIP fallbacks)

## Testing

Two demo scripts are provided:

**`examples/bsa_chunking_demo.py`** - Basic chunking functionality:
- Creates test files exceeding 2GB
- Demonstrates chunking functionality
- Shows CAO-style naming
- Validates integrity

**`examples/batch_repacker_chunking_demo.py`** - Batch repacker chunking:
- Creates large test mods
- Demonstrates batch processing with chunking
- Shows automatic chunk detection
- Validates batch workflow

## Configuration

The chunk size limit is configurable (default 2GB):
- `max_chunk_size_gb`: Maximum size per chunk in GB
- Can be adjusted based on tool requirements
- 2GB is optimal for most modding tools

## Backward Compatibility

- Existing single BSA creation still works for small archives
- Automatic detection of when chunking is needed
- No changes required to existing workflows
- ESP templates work with both single and chunked archives

## Technical Notes

- Uses temporary staging directories for each chunk
- Proper cleanup of temporary files
- Memory efficient processing
- Cross-platform compatibility
- Comprehensive logging and error reporting

This implementation ensures Safe Resource Packer creates archives that are compatible with all modding tools, preventing the PGPatcher errors you encountered while maintaining the same high-quality output.
