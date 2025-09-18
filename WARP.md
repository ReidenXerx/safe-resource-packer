# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Safe Resource Packer is a Python utility designed for game modding (particularly Skyrim/Fallout) that intelligently classifies generated resources to determine which files can be safely packed into archives vs. which should remain loose to preserve overrides. It uses SHA1 hash comparison and case-insensitive path matching to classify files into three categories: new (safe to pack), modified (keep loose), and identical (skip).

## Common Development Commands

### Package Installation & Setup
```bash
# Install in development mode (recommended)
pip install -e .

# Install from requirements.txt for enhanced CLI features
pip install -r requirements.txt

# Install basic version without enhanced dependencies
pip install .
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core.py -v

# Run tests with coverage
python -m pytest tests/ --cov=safe_resource_packer

# Run tests with debug output
python -m pytest tests/ -v -s
```

### Running the Tool
```bash
# Using console script entry point (after installation)
safe-resource-packer --source "./data" --generated "./generated" --output-pack "./pack" --output-loose "./loose"

# Using alternative entry point
srp --help

# Running directly from source (development)
python -m safe_resource_packer.cli --help

# Using Python API directly
python examples/basic_usage.py
python examples/skyrim_bodyslide_example.py
```

### Code Quality & Linting
```bash
# Format code with black (if installed)
black src/ tests/ examples/

# Type checking with mypy (if installed)
mypy src/

# Lint with flake8 (if installed)
flake8 src/ tests/
```

## Architecture & Code Structure

### Core Components

**SafeResourcePacker (core.py)**: Main orchestrator class that:
- Creates temporary copies of source files for safe processing
- Coordinates the classification process via PathClassifier
- Manages multi-threading and cleanup operations
- Provides the main API entry point for processing operations

**PathClassifier (classifier.py)**: File classification engine that:
- Discovers all files in the generated directory using recursive traversal
- Performs case-insensitive path matching against source directory
- Uses SHA1 hashing to compare file contents when matches are found  
- Classifies files as: NEW (pack-safe), MODIFIED (loose-override), IDENTICAL (skip)
- Handles multi-threaded processing with progress tracking

**CLI System (cli.py)**: Dual-mode command interface:
- Primary: Enhanced CLI with rich/colorama for better UX (falls back gracefully)
- Fallback: Basic CLI using only standard library argparse
- Provides console script entry points and argument validation

### Key Workflows

1. **Resource Processing Flow**:
   - Copy source directory to temporary location (safety measure)
   - Scan generated directory for all files recursively
   - For each generated file: find corresponding source file (case-insensitive)
   - Compare files via SHA1 hash if source match found
   - Copy files to appropriate output directory based on classification
   - Generate processing summary and logs

2. **File Classification Logic**:
   - Generated file exists, source file doesn't exist → NEW (safe to pack)
   - Generated file exists, source file exists, different hashes → MODIFIED (keep loose)
   - Generated file exists, source file exists, same hashes → IDENTICAL (skip processing)

### Package Structure
```
src/safe_resource_packer/     # Main package under src/ layout
├── __init__.py              # Package exports and metadata
├── core.py                  # SafeResourcePacker main class  
├── classifier.py            # PathClassifier file classification logic
├── cli.py                   # Command-line interface (dual-mode)
├── enhanced_cli.py          # Rich-enhanced CLI features
└── utils.py                 # Logging, progress, hashing utilities
```

## Development Patterns

### Error Handling
- All file operations use proper exception handling with detailed logging
- Temporary directories are always cleaned up via try/finally blocks
- Hash calculation failures are logged but don't stop processing
- Missing source/generated paths are validated upfront

### Multi-threading
- Uses ThreadPoolExecutor for file processing operations
- Thread count is configurable (default: 8 threads)
- Progress tracking is thread-safe using atomic counters
- File I/O operations are the main parallelized workload

### Logging System
- Custom logging utility with timestamp formatting
- Global debug mode toggle affects logging verbosity
- Logs accumulated in memory then written to file at end
- Separate tracking for skipped files and errors

### Testing Strategy
- Unit tests cover core functionality with temporary file fixtures
- Tests use small thread counts (2) to avoid overwhelming test environment
- Mock file scenarios: new files, identical files, modified files
- Cleanup verification ensures no temporary file leaks

## Key Configuration Points

### Entry Points (pyproject.toml/setup.py)
- `safe-resource-packer`: Main CLI entry point
- `srp`: Short alias for main CLI
- `safe-resource-packer-basic`: Direct access to basic CLI mode

### Dependencies
- **Core**: Uses only Python standard library (pathlib, hashlib, concurrent.futures, etc.)
- **Enhanced**: Optional rich, click, colorama for better CLI experience
- **Development**: pytest, black, mypy, flake8 for code quality

### Default Settings
- 8 processing threads (configurable via --threads)
- SHA1 hashing for file comparison
- Case-insensitive file matching for cross-platform compatibility
- Temporary directory cleanup on exit

## Common Debugging Scenarios

### File Permission Issues
Enable debug mode (`--debug`) and check logs for permission denied errors during file operations.

### Performance Issues
Monitor thread utilization - very high I/O workloads may benefit from more threads, CPU-bound tasks may need fewer.

### Path Matching Problems
Debug mode shows detailed path resolution attempts. Case sensitivity and path normalization are handled automatically.

### Hash Calculation Failures
Large files or permission issues can cause hash failures - these are logged but processing continues for other files.
