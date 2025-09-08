#!/usr/bin/env python3
"""
Batch Repacker Configuration Examples

This file shows how to customize the BatchModRepacker for different modding scenarios.
The system is designed to be highly flexible and avoid hardcoded values.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.batch_repacker import BatchModRepacker


def example_bodyslide_config():
    """
    Configuration optimized for BodySlide-generated mods.
    
    BodySlide often creates mods with specific folder structures and naming conventions.
    """
    config = {
        # BodySlide typically generates these folders
        'folder_categories': {
            'meshes': ['meshes', 'CalienteTools/BodySlide/SliderSets'],
            'textures': ['textures'],
            'scripts': ['scripts'],
            'other': ['CalienteTools', 'tools', 'fomod']
        },
        
        # BodySlide mods often have additional file types
        'asset_extensions': {
            'meshes': ['.nif', '.tri', '.hkx', '.obj'],
            'textures': ['.dds', '.tga', '.png'],
            'bodyslide': ['.osp', '.xml', '.nif'],  # BodySlide-specific
            'data': ['.txt', '.ini', '.json'],
            'other': ['.osd', '.slider']  # BodySlide sliders
        },
        
        # Custom naming for BodySlide collections
        'package_naming': {
            'use_esp_name': True,
            'suffix': '_BodySlide',
            'version': 'v1.0',
            'separator': '_'
        }
    }
    
    return BatchModRepacker(game_type='skyrim', config=config)


def example_fallout4_config():
    """
    Configuration optimized for Fallout 4 mods.
    
    Fallout 4 has different file structures and BA2 archives.
    """
    config = {
        # Fallout 4 specific plugin extensions
        'plugin_extensions': ['.esp', '.esl', '.esm', '.ba2'],
        
        # Fallout 4 asset categories
        'folder_categories': {
            'meshes': ['meshes', 'geometries'],
            'textures': ['textures', 'materials'], 
            'sounds': ['sound', 'music', 'voice'],
            'scripts': ['scripts', 'source'],
            'interface': ['interface', 'strings'],
            'animations': ['animationdata', 'animations'],
            'other': ['misc', 'lodsettings', 'programs']
        },
        
        # Fallout 4 specific file types
        'asset_extensions': {
            'meshes': ['.nif', '.tri', '.hkx', '.bgsm', '.bgem'],
            'textures': ['.dds', '.tga', '.png'],
            'audio': ['.wav', '.xwm', '.fuz'],
            'scripts': ['.pex', '.psc'],
            'interface': ['.swf', '.gfx', '.strings'],
            'data': ['.txt', '.ini', '.json', '.xml'],
            'other': ['.ba2', '.cdx', '.lip']
        },
        
        # Fallout 4 package naming
        'package_naming': {
            'use_esp_name': True,
            'suffix': '_F4',
            'version': 'v1.0',
            'separator': '_'
        }
    }
    
    return BatchModRepacker(game_type='fallout4', config=config)


def example_texture_pack_config():
    """
    Configuration optimized for texture pack collections.
    
    Texture packs often have deep folder hierarchies and many file formats.
    """
    config = {
        # Focus on texture-heavy mods
        'folder_categories': {
            'textures': ['textures', 'texture', 'tex', 'materials', 'material', 'diffuse', 'normal', 'specular'],
            'meshes': ['meshes', 'mesh', 'models'],
            'other': ['readme', 'docs', 'screenshots']
        },
        
        # Comprehensive texture formats
        'asset_extensions': {
            'textures': ['.dds', '.tga', '.bmp', '.png', '.jpg', '.jpeg', '.tiff', '.hdr', '.exr'],
            'meshes': ['.nif', '.obj'],
            'data': ['.txt', '.ini', '.json', '.readme', '.md'],
            'other': []
        },
        
        # Texture pack naming
        'package_naming': {
            'use_esp_name': True,
            'suffix': '_TexturePack',
            'version': 'v2K',  # Common for texture resolutions
            'separator': '_'
        },
        
        # Allow deeper scanning for texture hierarchies
        'processing': {
            'max_depth': 15,
            'min_assets': 5,  # Texture packs should have multiple textures
            'case_sensitive': False
        }
    }
    
    return BatchModRepacker(game_type='skyrim', config=config)


def example_script_mod_config():
    """
    Configuration optimized for script-heavy mods.
    
    Script mods often have source files and compiled scripts.
    """
    config = {
        # Script-focused categories
        'folder_categories': {
            'scripts': ['scripts', 'script', 'source', 'src', 'papyrus'],
            'interface': ['interface', 'ui', 'mcm'],  # MCM configs
            'data': ['data', 'config', 'strings', 'translation'],
            'other': ['docs', 'readme']
        },
        
        # Script file extensions
        'asset_extensions': {
            'scripts': ['.pex', '.psc', '.papyrus', '.skse', '.f4se', '.dll'],
            'interface': ['.swf', '.gfx', '.menu', '.translation', '.strings'],
            'data': ['.txt', '.ini', '.json', '.yaml', '.xml', '.cfg'],
            'other': ['.readme', '.md', '.pdf']
        },
        
        # Script mod naming
        'package_naming': {
            'use_esp_name': True,
            'suffix': '_Script',
            'version': 'v1.0',
            'separator': '_'
        }
    }
    
    return BatchModRepacker(game_type='skyrim', config=config)


def example_custom_game_config():
    """
    Example configuration for a custom game or modding framework.
    
    Shows how to completely customize for non-standard scenarios.
    """
    config = {
        # Custom plugin extensions (maybe for a different game engine)
        'plugin_extensions': ['.mod', '.plugin', '.pak', '.data'],
        
        # Custom folder structure
        'folder_categories': {
            'assets': ['assets', 'content', 'resources'],
            'graphics': ['graphics', 'gfx', 'images'],
            'audio': ['audio', 'sounds', 'music'],
            'code': ['code', 'logic', 'behavior'],
            'config': ['config', 'settings', 'params'],
            'other': []
        },
        
        # Custom file types
        'asset_extensions': {
            'graphics': ['.png', '.jpg', '.tga', '.bmp', '.webp'],
            'audio': ['.wav', '.ogg', '.mp3', '.flac'],
            'code': ['.lua', '.js', '.py', '.cs'],
            'data': ['.json', '.xml', '.yaml', '.toml'],
            'other': ['.bin', '.dat', '.res']
        },
        
        # Custom naming scheme
        'package_naming': {
            'use_esp_name': False,  # Use folder name instead
            'suffix': '_Mod',
            'version': 'v1.0.0',
            'separator': '-'  # Use dash instead of underscore
        },
        
        # Custom processing options
        'processing': {
            'max_depth': 20,
            'min_assets': 1,
            'case_sensitive': True,  # Some systems are case-sensitive
            'follow_symlinks': True,
            'skip_hidden': False
        }
    }
    
    return BatchModRepacker(game_type='custom', config=config)


def demo_configuration_usage():
    """
    Demonstrate how to use different configurations.
    """
    print("🎯 Batch Repacker Configuration Examples")
    print("="*50)
    
    # Example 1: BodySlide configuration
    print("\n1. BodySlide Configuration:")
    bodyslide_repacker = example_bodyslide_config()
    print(f"   Plugin extensions: {bodyslide_repacker.config['plugin_extensions']}")
    print(f"   Package suffix: {bodyslide_repacker.config['package_naming']['suffix']}")
    
    # Example 2: Fallout 4 configuration  
    print("\n2. Fallout 4 Configuration:")
    f4_repacker = example_fallout4_config()
    print(f"   Game type: {f4_repacker.game_type}")
    print(f"   Mesh extensions: {f4_repacker.config['asset_extensions']['meshes']}")
    
    # Example 3: Texture pack configuration
    print("\n3. Texture Pack Configuration:")
    texture_repacker = example_texture_pack_config()
    print(f"   Max depth: {texture_repacker.config['processing']['max_depth']}")
    print(f"   Texture extensions: {texture_repacker.config['asset_extensions']['textures']}")
    
    # Example 4: Runtime configuration override
    print("\n4. Runtime Configuration Override:")
    custom_config = {
        'package_naming': {
            'suffix': '_CustomSuffix',
            'version': 'v2.5'
        },
        'processing': {
            'min_assets': 10  # Only process mods with 10+ assets
        }
    }
    
    custom_repacker = BatchModRepacker(game_type='skyrim', config=custom_config)
    print(f"   Custom suffix: {custom_repacker.config['package_naming']['suffix']}")
    print(f"   Min assets: {custom_repacker.config['processing']['min_assets']}")
    
    print("\n✅ Configuration system allows maximum flexibility!")
    print("   • No hardcoded file extensions")
    print("   • No hardcoded folder names") 
    print("   • No hardcoded naming patterns")
    print("   • Fully customizable for any modding scenario")


if __name__ == "__main__":
    demo_configuration_usage()
