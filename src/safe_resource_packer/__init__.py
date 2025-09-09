"""
Safe Resource Packer - A secure and efficient resource packing utility.

This package provides tools for safely packing resources while detecting
overrides and preventing conflicts, particularly useful for Skyrim modding
and similar use cases.
"""

__version__ = "1.0.0"
__author__ = "Vadim"
__email__ = ""
__description__ = "A secure and efficient resource packing utility for embedding files into executables"

from .core import SafeResourcePacker
from .classifier import PathClassifier
from .batch_repacker import BatchModRepacker
from .dynamic_progress import log, print_progress
from .utils import file_hash

__all__ = [
    "SafeResourcePacker",
    "PathClassifier",
    "BatchModRepacker",
    "log",
    "print_progress",
    "file_hash"
]
