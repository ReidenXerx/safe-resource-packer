# ESP Templates

This directory contains template ESP files for different games. These templates are used by the packaging system to create dummy ESP files that load BSA/BA2 archives.

## 🎯 Included Templates

✅ **skyrim_template.esp** - Template for Skyrim Special Edition
✅ **fallout4_template.esp** - Template for Fallout 4

These templates are **ready to use** and will work out of the box! No additional setup required.

## 🚀 How It Works

The packaging system automatically:

1. Detects your game type (`--game-type skyrim` or `--game-type fallout4`)
2. Uses the appropriate template
3. Copies and renames it to match your mod name
4. Creates a working ESP that loads your BSA/BA2 archives

## 📦 Template Usage

**Automatic (Recommended):**

```bash
# Uses skyrim_template.esp automatically
safe-resource-packer --package ./MyMod --mod-name "AwesomeMod" --game-type skyrim

# Uses fallout4_template.esp automatically
safe-resource-packer --package ./MyMod --mod-name "AwesomeMod" --game-type fallout4
```

**Custom Template:**

```bash
# Use your own template if needed
safe-resource-packer --package ./MyMod --mod-name "AwesomeMod" --esp-template ./my_custom.esp
```

## ✨ Template Quality

These templates are:

-   ✅ **Tested and verified** for compatibility
-   ✅ **Minimal size** for optimal performance
-   ✅ **Proper headers** (TES4/TES5 format)
-   ✅ **Game engine compatible**

## 🔧 Adding Custom Templates

To add your own ESP template:

1. Place your template ESP file in this directory
2. Name it according to the pattern: `{game_type}_template.esp`
    - Example: `skyrim_template.esp`, `fallout4_template.esp`

## Template Requirements

Your ESP template should:

-   Be a minimal, working ESP file for the target game
-   Have proper headers (TES4/TES5)
-   Be as small as possible (dummy content only)
-   Be compatible with the target game engine

## Using Templates

The packaging system will automatically:

1. Copy your template
2. Rename it to match the mod name
3. Reference the created BSA/BA2 archives

## Example Template Creation

### For Skyrim:

1. Open Creation Kit
2. Create new ESP
3. Save without adding any content
4. Copy to this directory as `skyrim_template.esp`

### For Fallout 4:

1. Open Creation Kit
2. Create new ESP
3. Save without adding any content
4. Copy to this directory as `fallout4_template.esp`

## Providing Templates via CLI

You can also provide templates when building packages:

```bash
safe-resource-packer --source ./data --generated ./bodyslide --package ./output --esp-template ./my_template.esp
```
