"""
First-time user detection and experience level assessment.

This module determines if a user is new to the tool and what their experience level
is, allowing us to provide appropriate guidance and tutorials.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


class FirstTimeDetector:
    """Detects first-time users and manages user experience profiles."""
    
    def __init__(self):
        """Initialize the first-time detector."""
        self.config_dir = Path.home() / '.safe_resource_packer'
        self.config_file = self.config_dir / 'user_profile.json'
        self.config_dir.mkdir(exist_ok=True)
        
    def is_first_time_user(self) -> bool:
        """
        Check if this is the user's first time using the tool.
        
        Returns:
            True if this is a first-time user, False otherwise
        """
        return not self.config_file.exists()
    
    def get_user_experience_level(self) -> str:
        """
        Get the user's experience level.
        
        Returns:
            Experience level: 'beginner', 'intermediate', or 'advanced'
        """
        if self.is_first_time_user():
            return 'beginner'
            
        profile = self.load_user_profile()
        return profile.get('experience_level', 'intermediate')
    
    def get_preferred_mod_manager(self) -> Optional[str]:
        """
        Get the user's preferred mod manager.
        
        Returns:
            Mod manager preference: 'MO2', 'Vortex', 'Manual', or None
        """
        if self.is_first_time_user():
            return None
            
        profile = self.load_user_profile()
        return profile.get('mod_manager')
    
    def get_usage_count(self) -> int:
        """
        Get how many times the user has used the tool.
        
        Returns:
            Number of times the tool has been used
        """
        if self.is_first_time_user():
            return 0
            
        profile = self.load_user_profile()
        return profile.get('usage_count', 0)
    
    def load_user_profile(self) -> Dict[str, Any]:
        """
        Load the user's profile from disk.
        
        Returns:
            User profile dictionary
        """
        if not self.config_file.exists():
            return {}
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If profile is corrupted, treat as first-time user
            return {}
    
    def save_user_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Save the user's profile to disk.
        
        Args:
            profile: User profile dictionary to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def update_usage_stats(self, completed_successfully: bool = True):
        """
        Update usage statistics for the user.
        
        Args:
            completed_successfully: Whether the operation completed successfully
        """
        profile = self.load_user_profile()
        
        # Update usage count
        profile['usage_count'] = profile.get('usage_count', 0) + 1
        profile['last_used'] = datetime.now().isoformat()
        
        # Update success rate
        if completed_successfully:
            profile['successful_runs'] = profile.get('successful_runs', 0) + 1
        
        # Auto-upgrade experience level based on usage
        usage_count = profile['usage_count']
        if usage_count >= 10 and profile.get('experience_level', 'beginner') == 'beginner':
            profile['experience_level'] = 'intermediate'
        elif usage_count >= 50 and profile.get('experience_level', 'intermediate') == 'intermediate':
            profile['experience_level'] = 'advanced'
        
        self.save_user_profile(profile)
    
    def set_user_preferences(self, 
                           experience_level: str = None,
                           mod_manager: str = None,
                           preferred_game: str = None,
                           tutorial_completed: bool = None):
        """
        Set user preferences and save to profile.
        
        Args:
            experience_level: User's experience level
            mod_manager: Preferred mod manager
            preferred_game: Most commonly used game
            tutorial_completed: Whether user completed the tutorial
        """
        profile = self.load_user_profile()
        
        if experience_level:
            profile['experience_level'] = experience_level
        if mod_manager:
            profile['mod_manager'] = mod_manager
        if preferred_game:
            profile['preferred_game'] = preferred_game
        if tutorial_completed is not None:
            profile['tutorial_completed'] = tutorial_completed
            
        # Set initial timestamp if this is first time
        if 'first_used' not in profile:
            profile['first_used'] = datetime.now().isoformat()
            
        self.save_user_profile(profile)
    
    def should_offer_tutorial(self) -> bool:
        """
        Determine if we should offer the tutorial to this user.
        
        Returns:
            True if tutorial should be offered, False otherwise
        """
        if self.is_first_time_user():
            return True
            
        profile = self.load_user_profile()
        
        # Offer tutorial if never completed and usage count is low
        if not profile.get('tutorial_completed', False) and profile.get('usage_count', 0) < 3:
            return True
            
        return False
    
    def get_welcome_message_type(self) -> str:
        """
        Determine what type of welcome message to show.
        
        Returns:
            Welcome message type: 'first_time', 'returning_beginner', 'experienced'
        """
        if self.is_first_time_user():
            return 'first_time'
            
        profile = self.load_user_profile()
        experience_level = profile.get('experience_level', 'beginner')
        usage_count = profile.get('usage_count', 0)
        
        if experience_level == 'beginner' or usage_count < 5:
            return 'returning_beginner'
        else:
            return 'experienced'
