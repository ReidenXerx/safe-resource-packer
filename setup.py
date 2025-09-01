"""Setup script for Safe Resource Packer."""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="safe-resource-packer",
    version="1.0.0",
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
        "License :: OSI Approved :: MIT License",
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
            "safe-resource-packer=safe_resource_packer.cli:main",
            "srp=safe_resource_packer.cli:main",
        ],
    },
    keywords="resource packing, file management, skyrim modding, game modding, file classification",
    include_package_data=True,
    zip_safe=False,
)
