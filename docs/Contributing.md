---
layout: default
title: Contributing
description: Guidelines for contributing to Safe Resource Packer
---

# Contributing to Safe Resource Packer

Thank you for your interest in contributing to Safe Resource Packer! This document provides guidelines and information for contributors.

## Getting Started

### Development Setup

1. **Fork and clone the repository**

    ```bash
    git clone https://github.com/yourusername/safe-resource-packer.git
    cd safe-resource-packer
    ```

2. **Create a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install development dependencies**

    ```bash
    pip install -e .
    pip install pytest pytest-cov black flake8 mypy
    ```

4. **Verify installation**
    ```bash
    safe-resource-packer --version
    python -m pytest tests/
    ```

## Development Workflow

### Branch Naming

Use descriptive branch names:

-   `feature/add-new-classifier`
-   `bugfix/fix-hash-calculation`
-   `docs/update-api-documentation`
-   `refactor/improve-error-handling`

### Making Changes

1. **Create a feature branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Make your changes**

    - Follow the code style guidelines (see below)
    - Add tests for new functionality
    - Update documentation as needed

3. **Test your changes**

    ```bash
    # Run all tests
    python -m pytest tests/ -v

    # Run with coverage
    python -m pytest tests/ --cov=safe_resource_packer

    # Run linting
    black src/ tests/ examples/
    flake8 src/ tests/
    mypy src/
    ```

4. **Commit your changes**

    ```bash
    git add .
    git commit -m "Add feature: descriptive commit message"
    ```

5. **Push and create pull request**
    ```bash
    git push origin feature/your-feature-name
    ```

## Code Style Guidelines

### Python Style

We follow PEP 8 with some specific preferences:

-   **Line length**: 88 characters (Black default)
-   **Imports**: Use absolute imports, group by standard library, third-party, local
-   **Docstrings**: Use Google-style docstrings
-   **Type hints**: Use type hints for function parameters and return values

### Code Formatting

Use Black for automatic code formatting:

```bash
black src/ tests/ examples/
```

### Linting

Use flake8 for linting:

```bash
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
```

### Type Checking

Use mypy for type checking:

```bash
mypy src/
```

### Example Code Style

```python
"""Module docstring describing the purpose."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from safe_resource_packer.utils import log


class ExampleClass:
    """Example class demonstrating code style.

    This class shows the preferred code style including docstrings,
    type hints, and formatting.
    """

    def __init__(self, threads: int = 8, debug: bool = False) -> None:
        """Initialize the example class.

        Args:
            threads: Number of threads to use for processing
            debug: Enable debug logging
        """
        self.threads = threads
        self.debug = debug

    def process_files(
        self,
        source_path: str,
        output_path: str
    ) -> Tuple[int, int]:
        """Process files from source to output.

        Args:
            source_path: Path to source files
            output_path: Path for output files

        Returns:
            Tuple of (processed_count, error_count)

        Raises:
            FileNotFoundError: If source_path doesn't exist
            PermissionError: If insufficient permissions
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")

        processed_count = 0
        error_count = 0

        # Implementation here
        log(f"Processed {processed_count} files")

        return processed_count, error_count
```

## Testing Guidelines

### Test Structure

-   Place tests in the `tests/` directory
-   Name test files with `test_` prefix
-   Use descriptive test method names
-   Group related tests in the same test class

### Writing Tests

```python
import unittest
import tempfile
import os
from safe_resource_packer.core import SafeResourcePacker


class TestSafeResourcePacker(unittest.TestCase):
    """Test SafeResourcePacker functionality."""

    def setUp(self):
        """Set up test fixtures before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.packer = SafeResourcePacker(threads=2, debug=True)

    def tearDown(self):
        """Clean up after each test."""
        self.packer.cleanup_temp()
        # Clean up temp_dir if needed

    def test_initialization(self):
        """Test packer initialization with custom parameters."""
        packer = SafeResourcePacker(threads=16, debug=False)
        self.assertEqual(packer.threads, 16)
        self.assertEqual(packer.debug, False)

    def test_process_resources_with_valid_paths(self):
        """Test resource processing with valid input paths."""
        # Create test files and directories
        # ... setup code ...

        # Test the functionality
        pack_count, loose_count, skip_count = self.packer.process_resources(
            source_path=source_dir,
            generated_path=generated_dir,
            output_pack=pack_dir,
            output_loose=loose_dir
        )

        # Verify results
        self.assertGreater(pack_count, 0)
        self.assertTrue(os.path.exists(pack_dir))
```

### Test Coverage

Aim for high test coverage:

```bash
# Run tests with coverage report
python -m pytest tests/ --cov=safe_resource_packer --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Documentation Guidelines

### Code Documentation

-   Use Google-style docstrings for all public functions and classes
-   Include parameter types and descriptions
-   Document return values and exceptions
-   Provide usage examples for complex functions

### User Documentation

-   Update README.md for user-facing changes
-   Update API.md for API changes
-   Update USAGE.md for new usage patterns
-   Include examples in the `examples/` directory

### Documentation Example

```python
def classify_by_path(
    self,
    source_root: str,
    generated_root: str,
    out_pack: str,
    out_loose: str,
    threads: int = 8
) -> Tuple[int, int, int]:
    """Classify all files in generated directory.

    This method processes all files in the generated directory and
    classifies them based on comparison with the source directory.
    Files are copied to appropriate output directories based on
    whether they are new, identical, or modified.

    Args:
        source_root: Root directory of source files
        generated_root: Root directory of generated files
        out_pack: Output directory for packable files
        out_loose: Output directory for loose files
        threads: Number of threads to use for processing

    Returns:
        Tuple of (pack_count, loose_count, skip_count) where:
        - pack_count: Number of files classified for packing
        - loose_count: Number of files classified as loose
        - skip_count: Number of files skipped (identical)

    Raises:
        FileNotFoundError: If source_root or generated_root don't exist
        PermissionError: If insufficient permissions for file operations

    Example:
        >>> classifier = PathClassifier(debug=True)
        >>> pack, loose, skip = classifier.classify_by_path(
        ...     "/path/to/source",
        ...     "/path/to/generated",
        ...     "./pack",
        ...     "./loose",
        ...     threads=12
        ... )
        >>> print(f"Pack: {pack}, Loose: {loose}, Skip: {skip}")
        Pack: 150, Loose: 25, Skip: 300
    """
```

## Pull Request Guidelines

### Before Submitting

1. **Ensure all tests pass**

    ```bash
    python -m pytest tests/
    ```

2. **Check code formatting**

    ```bash
    black --check src/ tests/ examples/
    flake8 src/ tests/
    ```

3. **Verify type hints**

    ```bash
    mypy src/
    ```

4. **Update documentation**
    - Update docstrings for new/modified functions
    - Update user documentation if needed
    - Add examples if appropriate

### Pull Request Template

When creating a pull request, include:

```markdown
## Description

Brief description of changes made.

## Type of Change

-   [ ] Bug fix (non-breaking change that fixes an issue)
-   [ ] New feature (non-breaking change that adds functionality)
-   [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
-   [ ] Documentation update

## Testing

-   [ ] Added tests for new functionality
-   [ ] All existing tests pass
-   [ ] Tested manually with example scenarios

## Checklist

-   [ ] Code follows the project's style guidelines
-   [ ] Self-review of the code completed
-   [ ] Code is commented, particularly in hard-to-understand areas
-   [ ] Documentation has been updated
-   [ ] Changes generate no new warnings
```

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

1. Run command '...'
2. With parameters '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**

-   OS: [e.g. Windows 10, Ubuntu 20.04]
-   Python version: [e.g. 3.9.7]
-   Safe Resource Packer version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Release Process

### Version Numbering

We use semantic versioning (SemVer):

-   MAJOR.MINOR.PATCH (e.g., 1.2.3)
-   MAJOR: Breaking changes
-   MINOR: New features (backward compatible)
-   PATCH: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers in:

    - `src/safe_resource_packer/__init__.py`
    - `setup.py`
    - `pyproject.toml`

2. Update CHANGELOG.md with new features and fixes

3. Run full test suite and ensure all tests pass

4. Create release branch and pull request

5. After merge, create GitHub release with tag

## Community Guidelines

### Code of Conduct

-   Be respectful and inclusive
-   Focus on constructive feedback
-   Help newcomers learn and contribute
-   Follow the project's technical standards

### Communication

-   Use GitHub issues for bug reports and feature requests
-   Use GitHub discussions for general questions
-   Be clear and specific in issue descriptions
-   Provide minimal reproducible examples when possible

## Recognition

Contributors will be recognized in:

-   CONTRIBUTORS.md file
-   GitHub contributors page
-   Release notes for significant contributions

Thank you for contributing to Safe Resource Packer!
