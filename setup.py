"""Setup script for Safe Resource Packer."""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py without importing
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'safe_resource_packer', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
        if match:
            return match.group(1)
        raise RuntimeError('Unable to find version string.')

__version__ = get_version()

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        # Fallback to hardcoded requirements if requirements.txt is not available
        return [
            "rich>=13.0.0",
            "click>=8.0.0", 
            "colorama>=0.4.4",
            "psutil>=5.8.0"
        ]

setup(
    name="safe-resource-packer",
    version=__version__,  # Read from __init__.py
    author="Dudu",

    description="A secure and efficient resource packing utility for embedding files into executables",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/safe-resource-packer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/safe-resource-packer/issues",
        "Documentation": "https://github.com/yourusername/safe-resource-packer/blob/main/docs/",
        "Source Code": "https://github.com/yourusername/safe-resource-packer",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "safe-resource-packer=safe_resource_packer.enhanced_cli:enhanced_main",
            "safe-resource-packer-ui=safe_resource_packer.console_ui:run_console_ui",
        ],
    },
    keywords="resource packing, file management, skyrim modding, game modding, file classification",
    include_package_data=True,
    zip_safe=False,
)
