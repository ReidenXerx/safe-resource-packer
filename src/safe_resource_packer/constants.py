"""
Global constants for Safe Resource Packer.

This module contains configuration constants used throughout the application,
including blacklisted folders that should never be packed into BSA/BA2 archives.
"""

# Folders that should NEVER be packed into BSA/BA2 archives
# These folders must remain loose alongside the BSA/BA2 and plugin files
UNPACKABLE_FOLDERS = {
    'CalienteTools',

    # Mod manager and installation folders
    'FOMOD',
    'fomod',
    'META',
    'meta',
    
    # Script extender folders
    'SKSE',
    'skse',
    'SKSE64',
    'skse64',
    'F4SE',
    'f4se',
    
    # Mod configuration folders
    'MCM',
    'mcm',
    'Config',
    'config',
    'Settings',
    'settings',
    
    # Documentation and readme folders
    'Docs',
    'docs',
    'Documentation',
    'documentation',
    'Readme',
    'readme',
    'README',
    
    # Source and development folders
    'Source',
    'source',
    'src',
    'SRC',
    'Development',
    'development',
    'dev',
    'DEV',
    
    # Backup and version folders
    'Backup',
    'backup',
    'Old',
    'old',
    'Archive',
    'archive',
    'Versions',
    'versions',
    
    # Tool-specific folders
    'Tools',
    'tools',
    'Utilities',
    'utilities',
    'Patches',
    'patches',
    
    # Mod-specific folders that should stay loose
    'Interface',
    'interface',
    'Menus',
    'menus',
    'Scripts',
    'scripts',
    'Translations',
    'translations',
    'Localization',
    'localization',
    
    # Game-specific folders that should stay loose
    'INI',
    'ini',
    'INI Files',
    'ini files',
    'Presets',
    'presets',
    'Profiles',
    'profiles',
}

# Additional folders that might be blacklisted based on game type
GAME_SPECIFIC_UNPACKABLE_FOLDERS = {
    'skyrim': {
        'SKSE',
        'skse',
        'SKSE64',
        'skse64',
        'MCM',
        'mcm',
    },
    'fallout4': {
        'F4SE',
        'f4se',
        'MCM',
        'mcm',
    },
    'fallout3': set(),  # No specific folders for FO3
    'falloutnv': set(),  # No specific folders for FONV
    'oblivion': set(),   # No specific folders for Oblivion
}

def get_unpackable_folders(game_type: str = None) -> set:
    """
    Get the complete set of unpackable folder names.
    
    Args:
        game_type: Optional game type to include game-specific folders
        
    Returns:
        Set of folder names that should never be packed
    """
    unpackable = UNPACKABLE_FOLDERS.copy()
    
    if game_type and game_type.lower() in GAME_SPECIFIC_UNPACKABLE_FOLDERS:
        unpackable.update(GAME_SPECIFIC_UNPACKABLE_FOLDERS[game_type.lower()])
    
    return unpackable

def is_unpackable_folder(folder_name: str, game_type: str = None) -> bool:
    """
    Check if a folder should remain unpacked.
    
    Args:
        folder_name: Name of the folder to check
        game_type: Optional game type for game-specific checks
        
    Returns:
        True if the folder should remain unpacked, False otherwise
    """
    unpackable_folders = get_unpackable_folders(game_type)
    return folder_name in unpackable_folders

def get_packable_folders(folder_names: list, game_type: str = None) -> list:
    """
    Filter a list of folder names to only include packable ones.
    
    Args:
        folder_names: List of folder names to filter
        game_type: Optional game type for game-specific checks
        
    Returns:
        List of folder names that can be packed
    """
    unpackable_folders = get_unpackable_folders(game_type)
    return [folder for folder in folder_names if folder not in unpackable_folders]

def get_unpackable_folders_from_list(folder_names: list, game_type: str = None) -> list:
    """
    Get the unpackable folders from a list of folder names.
    
    Args:
        folder_names: List of folder names to check
        game_type: Optional game type for game-specific checks
        
    Returns:
        List of folder names that should remain unpacked
    """
    unpackable_folders = get_unpackable_folders(game_type)
    return [folder for folder in folder_names if folder in unpackable_folders]
