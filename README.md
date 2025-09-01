# Safe Resource Packer

A secure and efficient resource packing utility for game modding, particularly designed for Skyrim and similar games. This tool intelligently classifies generated resources (like BodySlide output) to determine which files can be safely packed into archives and which should remain as loose files to preserve overrides.

## 🎯 Key Features

-   **Intelligent File Classification**: Automatically determines which files are new (safe to pack) vs. overrides (should stay loose)
-   **Hash-Based Comparison**: Uses SHA1 hashing to detect identical vs. modified files
-   **Multi-threaded Processing**: Fast processing with configurable thread count
-   **Case-Insensitive Matching**: Works with mixed-case file systems and naming conventions
-   **Safe Temporary Processing**: Creates temporary copies to avoid modifying source files
-   **Comprehensive Logging**: Detailed logs with timestamps and progress tracking
-   **Cross-Platform**: Works on Windows, Linux, and macOS

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/safe-resource-packer.git
cd safe-resource-packer

# Install the package
pip install -e .

# Or install from PyPI (when published)
pip install safe-resource-packer
```

### Command Line Usage

```bash
# Basic usage
safe-resource-packer --source /path/to/skyrim/Data --generated /path/to/bodyslide/output --output-pack ./pack --output-loose ./loose

# With custom settings
safe-resource-packer --source ./data --generated ./generated --output-pack ./pack --output-loose ./loose --threads 16 --debug

# Show help
safe-resource-packer --help
```

### Python API Usage

```python
from safe_resource_packer import SafeResourcePacker

# Create packer instance
packer = SafeResourcePacker(threads=8, debug=True)

# Process resources
pack_count, loose_count, skip_count = packer.process_resources(
    source_path="/path/to/skyrim/Data",
    generated_path="/path/to/bodyslide/output",
    output_pack="./pack",
    output_loose="./loose"
)

print(f"Files to pack: {pack_count}")
print(f"Files to keep loose: {loose_count}")
print(f"Files skipped (identical): {skip_count}")
```

## 📖 How It Works

The Safe Resource Packer uses a three-step classification process:

1. **File Discovery**: Scans all files in the generated resources directory
2. **Path Matching**: For each generated file, searches for a corresponding file in the source directory using case-insensitive matching
3. **Classification Logic**:
    - **New files** (no match found) → Safe to pack into BSA/BA2 archives
    - **Identical files** (same hash) → Skip (no processing needed)
    - **Modified files** (different hash) → Keep as loose files (they're overrides)

## 🎮 Common Use Cases

### Skyrim BodySlide Processing

```bash
# Process BodySlide generated meshes and textures
safe-resource-packer \
  --source "C:\Games\Skyrim Special Edition\Data" \
  --generated "C:\Users\YourUser\Documents\My Games\Skyrim Special Edition\CalienteTools\BodySlide\ShapeData" \
  --output-pack "./skyrim_pack" \
  --output-loose "./skyrim_loose"
```

### Fallout 4 BodySlide Processing

```bash
# Process Fallout 4 BodySlide output
safe-resource-packer \
  --source "C:\Games\Fallout 4\Data" \
  --generated "C:\Users\YourUser\Documents\My Games\Fallout 4\F4SE\Plugins\BodySlide\ShapeData" \
  --output-pack "./fo4_pack" \
  --output-loose "./fo4_loose"
```

## 📁 Project Structure

```
safe-resource-packer/
├── src/safe_resource_packer/     # Main package
│   ├── __init__.py              # Package initialization
│   ├── core.py                  # Core SafeResourcePacker class
│   ├── classifier.py            # File classification logic
│   ├── utils.py                 # Utility functions
│   └── cli.py                   # Command-line interface
├── examples/                    # Usage examples
│   ├── basic_usage.py           # Basic API usage
│   ├── skyrim_bodyslide_example.py  # Skyrim-specific example
│   └── config_example.py        # Configuration-based usage
├── tests/                       # Unit tests
│   ├── test_core.py
│   ├── test_classifier.py
│   └── test_utils.py
├── docs/                        # Documentation
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── pyproject.toml              # Modern Python packaging
└── README.md                   # This file
```

## 🔧 Configuration Options

| Option           | Description                                               | Default                    |
| ---------------- | --------------------------------------------------------- | -------------------------- |
| `--source`       | Path to reference/source files (e.g., Skyrim Data folder) | Required                   |
| `--generated`    | Path to generated files (e.g., BodySlide output)          | Required                   |
| `--output-pack`  | Directory for files safe to pack into archives            | Required                   |
| `--output-loose` | Directory for files that should stay loose                | Required                   |
| `--threads`      | Number of processing threads                              | 8                          |
| `--debug`        | Enable detailed debug logging                             | False                      |
| `--log`          | Log file path                                             | `safe_resource_packer.log` |

## 📊 Understanding the Output

After processing, you'll see a summary like this:

```
===== SUMMARY =====
Classified for packing (new): 1,247
Classified for loose (override): 89
Skipped (identical): 2,156
Skipped or errored: 3
```

-   **Pack files**: New files that can be safely packed into BSA/BA2 archives
-   **Loose files**: Modified files that override existing content and should stay loose
-   **Skipped files**: Identical files that don't need processing
-   **Errors**: Files that couldn't be processed (check the log)

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=safe_resource_packer

# Run specific test file
python -m pytest tests/test_core.py -v
```

## 📚 Examples

Check the `examples/` directory for detailed usage examples:

-   `basic_usage.py`: Simple API usage
-   `skyrim_bodyslide_example.py`: Skyrim-specific processing
-   `config_example.py`: Configuration-based processing with multiple scenarios

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   Designed for the Skyrim and Fallout modding communities
-   Inspired by the need for safe BSA/BA2 packing workflows
-   Built with Python's robust standard library

## ⚠️ Important Notes

-   **Always backup your files** before processing
-   The tool creates temporary copies and doesn't modify source files
-   Generated files in the "pack" directory can be safely archived
-   Generated files in the "loose" directory should remain as loose files
-   Check the log file for any errors or skipped files

## 🔗 Links

-   [GitHub Repository](https://github.com/yourusername/safe-resource-packer)
-   [Issue Tracker](https://github.com/yourusername/safe-resource-packer/issues)
-   [Documentation](docs/)

---

Made with ❤️ for the modding community
