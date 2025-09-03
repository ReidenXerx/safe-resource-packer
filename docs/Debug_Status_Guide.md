---
layout: default
title: Debug Status Guide
description: Understanding debug status messages during file classification
---

# Debug Status Guide

When running Safe Resource Packer in debug mode (`--debug`), you'll see detailed status messages for every file processed. This guide explains what each status means and why files are classified the way they are.

## 🎨 Color-Coded Status Messages

Debug mode uses color-coded messages to make it easy to understand what's happening:

- 🔍 **Green** = MATCH FOUND (file exists in source)
- 📦 **Blue** = NO MATCH (new file, pack it)
- ⏭️ **Yellow** = SKIP (identical file)
- 📁 **Magenta** = OVERRIDE (modified file, keep loose)
- ❌ **Red** = ERROR (copy/hash failures)
- ℹ️ **Cyan** = INFO (general information)
- ✅ **Green** = SUCCESS (operation completed)

## 📋 Status Message Meanings

### 🔍 `[MATCH FOUND]` (Green)
**What it means:** A file with the same path exists in your source directory.

**Example:**
```
🔍 [MATCH FOUND] meshes/armor/mymod/chest.nif matched to C:\Skyrim\Data\meshes\armor\mymod\chest.nif
```

**What happens next:** The tool will compare the file contents (hash) to determine if they're identical or different.

### 📦 `[NO MATCH]` (Blue)
**What it means:** This file doesn't exist in your source directory - it's completely new content.

**Example:**
```
📦 [NO MATCH] meshes/armor/mymod/new_armor.nif → pack
```

**What happens next:** The file is copied to the **pack** directory because it's safe to archive (no conflicts possible).

### ⏭️ `[SKIP]` (Yellow)
**What it means:** The file is identical to the source file - no processing needed.

**Example:**
```
⏭️ [SKIP] meshes/armor/mymod/chest.nif identical
```

**What happens next:** The file is ignored completely. It's redundant since the original already exists.

### 📁 `[OVERRIDE]` (Magenta)
**What it means:** The file exists in source but has different content - it's an override.

**Example:**
```
📁 [OVERRIDE] meshes/armor/mymod/chest.nif differs
```

**What happens next:** The file is copied to the **loose** directory because it must stay loose to override the original.

### ❌ `[COPY FAIL]` (Red)
**What it means:** Failed to copy a file to the output directory.

**Example:**
```
❌ [COPY FAIL] meshes/armor/mymod/large_file.nif: Disk full
```

**Common causes:**
- Disk space full
- Permission denied
- File locked by another process
- Invalid path characters

### 💥 `[HASH FAIL]` (Red)
**What it means:** Failed to calculate the file hash (checksum).

**Example:**
```
💥 [HASH FAIL] meshes/armor/mymod/corrupted.nif: Permission denied
```

**Common causes:**
- File corrupted
- Permission denied
- File locked
- File doesn't exist

### ⚠️ `[EXCEPTION]` (Red)
**What it means:** An unexpected error occurred while processing the file.

**Example:**
```
⚠️ [EXCEPTION] meshes/armor/mymod/weird_file.nif: UnicodeDecodeError
```

**Common causes:**
- File encoding issues
- Memory errors
- Unexpected file formats
- System errors

## 🔄 The Classification Process

Here's how Safe Resource Packer decides what to do with each file:

```
1. 🔍 Check if file exists in source directory
   ↓
2. If NO MATCH found:
   📦 → Copy to PACK directory (safe to archive)
   ↓
3. If MATCH FOUND:
   🔍 → Calculate hash of both files
   ↓
4. If hashes are identical:
   ⏭️ → SKIP (no processing needed)
   ↓
5. If hashes are different:
   📁 → Copy to LOOSE directory (override)
```

## 📊 Understanding the Results

After processing, you'll see a summary like this:

```
📦 Pack files (blue): 1,234
📁 Loose files (magenta): 89
⏭️ Skipped files (yellow): 2,156
❌ Errors: 3
```

### What Each Number Means:

- **Pack files:** New content that's safe to put in BSA/BA2 archives
- **Loose files:** Overrides that must stay loose (ESP files depend on them)
- **Skipped files:** Identical copies that waste space (good to skip!)
- **Errors:** Files that couldn't be processed (check the log for details)

## 🎯 Why This Classification Matters

### For Performance:
- **Pack files** → Go in archives for 3x faster loading
- **Loose files** → Stay loose to preserve overrides
- **Skip files** → Don't waste space on duplicates

### For Mod Compatibility:
- **Pack files** → Won't conflict with anything (they're new)
- **Loose files** → Override existing content (must stay loose)
- **Skip files** → Don't need to exist (original is already there)

## 🔧 Troubleshooting Common Issues

### High Error Count?
- Check disk space
- Verify file permissions
- Ensure files aren't locked by other programs
- Look for corrupted files

### Too Many Loose Files?
- This might be normal if you have many overrides
- Consider if you really need all those overrides
- Check if some files could be packed instead

### Too Many Skipped Files?
- This is usually good! It means you're not duplicating content
- Skipped files save space and improve performance

## 📝 Log File Details

All debug messages are saved to a log file for later review:

```
[2025-01-20 15:30:45] Starting Safe Resource Packer...
[2025-01-20 15:30:45] Source: C:\Games\Skyrim Special Edition\Data
[2025-01-20 15:30:45] Generated: C:\BodySlide\Output
[2025-01-20 15:30:45] Output Pack: ./pack
[2025-01-20 15:30:45] Output Loose: ./loose
[2025-01-20 15:30:45] Threads: 8
[2025-01-20 15:30:45] Debug: True
[2025-01-20 15:30:46] Classifying generated files by path override logic...
[2025-01-20 15:30:47] 🔍 [MATCH FOUND] meshes/armor/mymod/chest.nif matched to C:\Skyrim\Data\meshes\armor\mymod\chest.nif
[2025-01-20 15:30:47] 📁 [OVERRIDE] meshes/armor/mymod/chest.nif differs
[2025-01-20 15:30:48] 📦 [NO MATCH] meshes/armor/mymod/new_armor.nif → pack
[2025-01-20 15:30:49] ⏭️ [SKIP] meshes/armor/mymod/helmet.nif identical
[2025-01-20 15:30:50] ✅ Processing completed successfully!
```

## 🚀 Pro Tips

1. **Use debug mode sparingly** - it's very verbose but great for troubleshooting
2. **Check the log file** if you have errors - it contains detailed information
3. **High skip counts are good** - they mean you're not duplicating content
4. **Loose files are normal** - they're your overrides and must stay loose
5. **Pack files are safe** - they're new content that won't conflict

---

*This guide helps you understand what Safe Resource Packer is doing with each file during the classification process. The color-coded debug output makes it easy to see at a glance what's happening with your files.*
