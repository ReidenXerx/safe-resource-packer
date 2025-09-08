# 🔧 Flexible Configuration System - Zero Hardcoding

## 🎯 **Problem Solved**

You were absolutely right! The modding community is incredibly diverse, and **hardcoded values kill flexibility**. We've completely eliminated hardcoding from the Batch Mod Repacker to make it work with ANY modding scenario.

## ❌ **What We REMOVED (Hardcoded Values)**

### **Before: Hardcoded and Inflexible**
```python
# ❌ HARDCODED - Only worked for standard Skyrim mods
if file_lower.endswith(('.esp', '.esl', '.esm')):  # Fixed extensions
if rel_path.startswith('meshes/'):                 # Fixed folder names  
if rel_path.startswith('textures/'):               # Fixed folder names
final_package_name = f"{mod_name}_Repacked.7z"    # Fixed naming pattern
asset_extensions = {'.nif', '.dds', '.wav'}        # Fixed file types
```

### **After: Fully Configurable**
```python
# ✅ FLEXIBLE - Works with ANY extensions, folders, naming
for ext in self.config['plugin_extensions']:       # User-defined extensions
for category, patterns in self.config['folder_categories'].items():  # User-defined folders
final_package_name = f"{base_name}{separator}{version}{suffix}.7z"   # User-defined naming
for category, extensions in self.config['asset_extensions'].items(): # User-defined file types
```

## ✅ **What We ADDED (Flexible Configuration)**

### **1. Configurable Plugin Extensions**
```python
# Default supports multiple games and custom formats
'plugin_extensions': ['.esp', '.esl', '.esm', '.esp32', '.esm32', '.mod', '.plugin']

# Users can add their own:
config = {'plugin_extensions': ['.mymod', '.customplugin']}
```

### **2. Configurable Asset Extensions**
```python
# Comprehensive and expandable
'asset_extensions': {
    'meshes': ['.nif', '.tri', '.hkx', '.obj', '.fbx', '.dae'],
    'textures': ['.dds', '.tga', '.png', '.jpg', '.hdr', '.exr'],  
    'audio': ['.wav', '.mp3', '.ogg', '.xwm', '.fuz', '.flac'],
    'custom_category': ['.myformat', '.specialfile']  # Users can add categories
}
```

### **3. Configurable Folder Patterns**
```python
# No more hardcoded folder names!
'folder_categories': {
    'meshes': ['meshes', 'mesh', 'models', '3d', 'geometry'],
    'textures': ['textures', 'tex', 'materials', 'diffuse'],
    'sounds': ['sounds', 'audio', 'music', 'voice', 'sfx'],
    'custom': ['mycustomfolder', 'specialassets']  # Any folder structure
}
```

### **4. Configurable Package Naming**
```python
# Flexible naming patterns
'package_naming': {
    'use_esp_name': True,      # or False to use folder name
    'suffix': '_Repacked',     # Any suffix: '_BodySlide', '_4K', '_Custom'
    'version': 'v1.0',         # Any version: 'v2.5', 'Beta1', '2024'
    'separator': '_'           # Any separator: '_', '-', '.'
}
```

### **5. Configurable Processing Options**
```python
'processing': {
    'max_depth': 10,           # How deep to scan folders
    'min_assets': 1,           # Minimum files needed
    'case_sensitive': False,   # Case handling
    'follow_symlinks': False,  # Symlink behavior  
    'skip_hidden': True       # Hidden file handling
}
```

## 🎮 **Real-World Flexibility Examples**

### **BodySlide Collections**
```python
config = {
    'folder_categories': {
        'meshes': ['meshes', 'CalienteTools/BodySlide/SliderSets'],
        'bodyslide': ['tools', 'slidersets']
    },
    'asset_extensions': {
        'bodyslide': ['.osp', '.xml', '.slider', '.osd']
    },
    'package_naming': {'suffix': '_BodySlide'}
}
```

### **Texture Packs**
```python
config = {
    'folder_categories': {
        'textures': ['textures', 'tex', '4K', '2K', 'diffuse', 'normal']
    },
    'processing': {'max_depth': 15},  # Deep folder hierarchies
    'package_naming': {'suffix': '_4K', 'version': '2024'}
}
```

### **Custom Game Mods**
```python
config = {
    'plugin_extensions': ['.mod', '.pak', '.data'],  # Custom game
    'folder_categories': {
        'assets': ['content', 'resources', 'gamedata']
    },
    'asset_extensions': {
        'custom': ['.bin', '.dat', '.res', '.asset']
    }
}
```

### **Script-Heavy Mods**
```python
config = {
    'folder_categories': {
        'scripts': ['scripts', 'src', 'papyrus', 'skse'],
        'interface': ['mcm', 'ui', 'strings']
    },
    'asset_extensions': {
        'scripts': ['.pex', '.psc', '.dll', '.asi']
    }
}
```

## 📁 **Configuration Methods**

### **1. Runtime Configuration**
```python
# Pass config directly
config = {'package_naming': {'suffix': '_MyMod'}}
repacker = BatchModRepacker(config=config)
```

### **2. JSON Configuration Files**
```python
# Load from JSON file
repacker = BatchModRepacker.create_from_config_file('my_config.json')
```

### **3. Predefined Configurations**
```python
# Use predefined configs for common scenarios
bodyslide_repacker = example_bodyslide_config()
fallout4_repacker = example_fallout4_config()
texture_repacker = example_texture_pack_config()
```

## 🔍 **Configuration File Example**

```json
{
  "description": "Custom configuration for my modding workflow",
  
  "plugin_extensions": [".esp", ".esl", ".esm", ".mymod"],
  
  "folder_categories": {
    "meshes": ["meshes", "3d", "models", "custom_meshes"],
    "textures": ["textures", "4k", "2k", "materials"],
    "custom": ["my_special_folder", "unique_assets"]
  },
  
  "asset_extensions": {
    "meshes": [".nif", ".obj", ".fbx"],
    "textures": [".dds", ".png", ".tga"],
    "custom": [".myformat", ".special"]
  },
  
  "package_naming": {
    "use_esp_name": true,
    "suffix": "_MyCollection",
    "version": "v2.5",
    "separator": "-"
  }
}
```

## 🚀 **Benefits of Zero Hardcoding**

### **✅ Universal Compatibility**
- Works with **any game** (Skyrim, Fallout, Oblivion, custom games)
- Supports **any file extensions** (standard or custom)
- Handles **any folder structure** (deep hierarchies, custom names)

### **✅ Community Adaptability**  
- **BodySlide users**: Custom folder patterns for generated mods
- **Texture artists**: Support for any resolution/format naming
- **Script modders**: Flexible source file handling
- **Tool creators**: Custom file format support

### **✅ Future-Proof**
- New games? Just add new extensions/patterns
- New tools? Update configuration, no code changes
- New workflows? Customize naming and processing rules

### **✅ Easy Customization**
- **No programming required** - just edit JSON files
- **Gradual customization** - override only what you need
- **Shareable configs** - distribute configurations with mod packs

## 📋 **Available Configuration Files**

1. **`configs/batch_repacker_default.json`** - Comprehensive defaults
2. **`examples/batch_repacker_config.py`** - Programming examples  
3. **Custom configs** - Create your own for specific workflows

## 🎯 **Result: Maximum Flexibility**

The Batch Mod Repacker now has **ZERO hardcoded values** and can adapt to:

- ✅ **Any game engine** (Creation Engine, Unity, Unreal, custom)
- ✅ **Any file extensions** (standard or completely custom)
- ✅ **Any folder structure** (flat, nested, or complex hierarchies)
- ✅ **Any naming convention** (underscore, dash, version patterns)
- ✅ **Any workflow** (BodySlide, texture packs, script mods, etc.)

**Perfect for the diverse modding community!** 🎉

---

## 💡 **Usage Examples**

### **Quick Start with Defaults**
```python
# Uses sensible defaults for most scenarios
repacker = BatchModRepacker()
```

### **Custom Configuration**
```python
# Override specific settings
config = {
    'package_naming': {'suffix': '_MyStyle'},
    'processing': {'min_assets': 5}
}
repacker = BatchModRepacker(config=config)
```

### **Load from File**
```python
# Use JSON configuration file
repacker = BatchModRepacker.create_from_config_file('my_config.json')
```

**The system is now infinitely flexible and ready for any modding scenario!** 🚀
