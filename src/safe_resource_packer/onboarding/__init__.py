"""
Onboarding system for new users.

This module provides user detection, profiling, and adaptive welcome experiences
to make the tool more accessible to beginners while maintaining power for experts.
"""

from .first_time_detector import FirstTimeDetector
from .user_profiler import UserProfiler
from .welcome_system import AdaptiveWelcome

__all__ = [
    "FirstTimeDetector",
    "UserProfiler", 
    "AdaptiveWelcome"
]
