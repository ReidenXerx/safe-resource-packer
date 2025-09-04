# 🔍 Classification Flow Diagram

_The "Smart Brain" Behind Safe Resource Packer_

## 🧠 **Complete Classification Decision Tree**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAFE RESOURCE PACKER CLASSIFICATION ENGINE                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📁 Input: Generated File (e.g., "meshes/armor/mymod/chest.nif")            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    STEP 1: PATH MATCHING                              │ │
│  │                                                                         │ │
│  │  🔍 Does this file exist in the source directory?                      │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐                    ┌─────────────────┐            │ │
│  │  │       YES        │                    │       NO        │            │ │
│  │  │  (File Found)    │                    │  (New File)      │            │ │
│  │  │  "This path      │                    │  "This path      │            │ │
│  │  │   exists in      │                    │   doesn't exist  │            │ │
│  │  │   source"        │                    │   in source"     │            │ │
│  │  └─────────────────┘                    └─────────────────┘            │ │
│  │           │                                        │                    │ │
│  │           ▼                                        ▼                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    STEP 2: HASH COMPARISON                       │   │ │
│  │  │                                                                   │   │ │
│  │  │  🔐 Calculate SHA1 hash of both files                             │   │ │
│  │  │                                                                   │   │ │
│  │  │  ┌─────────────────┐                    ┌─────────────────┐     │   │ │
│  │  │  │   IDENTICAL      │                    │   DIFFERENT      │     │   │ │
│  │  │  │   (Same Hash)    │                    │  (Different Hash)│     │   │ │
│  │  │  │  "Files are      │                    │  "Files are      │     │   │ │
│  │  │  │   exactly the    │                    │   different"     │     │   │ │
│  │  │  │   same"          │                    │                   │     │   │ │
│  │  │  └─────────────────┘                    └─────────────────┘     │   │ │
│  │  │           │                                        │               │   │ │
│  │  │           ▼                                        ▼               │   │ │
│  │  │  ┌─────────────────┐                    ┌─────────────────┐     │   │ │
│  │  │  │     SKIP         │                    │    OVERRIDE      │     │   │ │
│  │  │  │  (No Action)      │                    │   (Keep Loose)    │     │   │ │
│  │  │  │  "Don't waste     │                    │  "This file      │     │   │ │
│  │  │  │   space on        │                    │   overrides      │     │   │ │
│  │  │  │   duplicates"     │                    │   the original"  │     │   │ │
│  │  │  └─────────────────┘                    └─────────────────┘     │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│           │                                        │                        │
│           ▼                                        ▼                        │
│  ┌─────────────────┐                    ┌─────────────────┐                │
│  │     SKIP        │                    │      PACK       │                │
│  │  (Identical)     │                    │   (New Content)  │                │
│  │  "No action      │                    │  "Safe to put    │                │
│  │   needed"        │                    │   in archive"    │                │
│  └─────────────────┘                    └─────────────────┘                │
│           │                                        │                        │
│           ▼                                        ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           OUTPUT ACTIONS                               │ │
│  │                                                                         │ │
│  │  ⏭️ SKIP:     File is identical to source → No processing needed        │ │
│  │  📁 LOOSE:    File overrides source → Copy to loose files directory     │ │
│  │              (modified version of existing file)                        │ │
│  │  📦 PACK:     File is new content → Copy to pack files directory       │ │
│  │              (doesn't exist in source, safe to archive)                 │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Simplified Version (For Social Media)**

```
┌─────────────────────────────────────────────────────────────┐
│                    File Classification                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📁 Input File                                              │
│         │                                                   │
│         ▼                                                   │
│  🔍 Exists in source?                                       │
│         │                                                   │
│    ┌────┴────┐                                             │
│    │         │                                             │
│   YES       NO                                             │
│    │         │                                             │
│    ▼         ▼                                             │
│  🔐 Hash match?                                            │
│    │                                                       │
│ ┌──┴──┐                                                   │
│ │     │                                                   │
│YES   NO                                                   │
│ │     │                                                   │
│ ▼     ▼                                                   │
│⏭️   📁                                                   │
│SKIP  LOOSE                                                │
│      │                                                   │
│      ▼                                                   │
│    📦 PACK                                               │
│                                                             │
│  📁 LOOSE = Override (modified version)                    │
│  📦 PACK = New content (doesn't exist in source)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 **Color-Coded Status Messages**

| Status          | Color      | Icon                                 | Meaning                 | Action |
| --------------- | ---------- | ------------------------------------ | ----------------------- | ------ |
| `[MATCH FOUND]` | 🔍 Green   | File exists in source directory      | Proceed to hash check   |
| `[NO MATCH]`    | 📦 Blue    | New file, safe to pack               | Copy to pack directory  |
| `[SKIP]`        | ⏭️ Yellow  | Identical file, no processing needed | Skip file entirely      |
| `[OVERRIDE]`    | 📁 Magenta | Modified file, must stay loose       | Copy to loose directory |
| `[COPY FAIL]`   | ❌ Red     | Failed to copy file                  | Log error, continue     |
| `[HASH FAIL]`   | 💥 Red     | Failed to calculate file hash        | Log error, continue     |
| `[EXCEPTION]`   | ⚠️ Red     | Unexpected error occurred            | Log error, continue     |

## 📊 **Real-World Examples**

### **Example 1: Identical File (SKIP)**
```
Input: "meshes/armor/mymod/chest.nif"

Step 1: 🔍 Check if "C:\Skyrim\Data\meshes\armor\mymod\chest.nif" exists
Result: YES (file found)

Step 2: 🔐 Compare SHA1 hashes
- Source file hash: a1b2c3d4e5f6...
- Generated file hash: a1b2c3d4e5f6...
Result: IDENTICAL

Step 3: ⏭️ SKIP
Action: No processing needed (file is identical)
```

### **Example 2: Override File (LOOSE)**
```
Input: "textures/armor/mymod/chest.dds"

Step 1: 🔍 Check if "C:\Skyrim\Data\textures\armor\mymod\chest.dds" exists
Result: YES (file found)

Step 2: 🔐 Compare SHA1 hashes
- Source file hash: a1b2c3d4e5f6...
- Generated file hash: f6e5d4c3b2a1...
Result: DIFFERENT

Step 3: 📁 LOOSE
Action: Copy to loose files (this overrides the original)
```

### **Example 3: New Content (PACK)**
```
Input: "meshes/armor/mymod/new_armor.nif"

Step 1: 🔍 Check if "C:\Skyrim\Data\meshes\armor\mymod\new_armor.nif" exists
Result: NO (file not found)

Step 2: 🔐 No hash comparison needed
Result: NEW FILE

Step 3: 📦 PACK
Action: Copy to pack files (safe to archive)
```

## 🎯 **Why This Matters**

-   **SKIP files**: Save space and processing time
-   **LOOSE files**: Preserve overrides for mod compatibility
-   **PACK files**: Optimize for game performance
-   **Error handling**: Ensures robust processing

## 📋 **Key Concepts Summary**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KEY CLASSIFICATION CONCEPTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📁 LOOSE FILES = OVERRIDES                                                 │
│  • File exists in source directory                                          │
│  • But has different content (different hash)                              │
│  • This file OVERRIDES the original                                         │
│  • Must stay loose for mod compatibility                                   │
│  • Example: Modified texture that replaces the original                    │
│                                                                             │
│  📦 PACK FILES = NEW CONTENT                                               │
│  • File does NOT exist in source directory                                 │
│  • Completely new content                                                  │
│  • Safe to put in BSA/BA2 archives                                         │
│  • Example: New armor mesh that doesn't exist in base game                  │
│                                                                             │
│  ⏭️ SKIP FILES = IDENTICAL                                                 │
│  • File exists in source directory                                         │
│  • And has identical content (same hash)                                   │
│  • No processing needed - don't waste space                                │
│  • Example: Unmodified file that's identical to original                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

_This intelligent classification is what makes Safe Resource Packer so powerful - it automatically makes the right decisions for every file!_
