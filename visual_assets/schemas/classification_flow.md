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
│  │  │  └─────────────────┘                    └─────────────────┘     │   │ │
│  │  │           │                                        │               │   │ │
│  │  │           ▼                                        ▼               │   │ │
│  │  │  ┌─────────────────┐                    ┌─────────────────┐     │   │ │
│  │  │  │     SKIP         │                    │    OVERRIDE      │     │   │ │
│  │  │  │  (No Action)      │                    │   (Keep Loose)    │     │   │ │
│  │  │  └─────────────────┘                    └─────────────────┘     │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│           │                                        │                        │
│           ▼                                        ▼                        │
│  ┌─────────────────┐                    ┌─────────────────┐                │
│  │     SKIP        │                    │      PACK       │                │
│  │  (Identical)     │                    │   (New Content)  │                │
│  └─────────────────┘                    └─────────────────┘                │
│           │                                        │                        │
│           ▼                                        ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           OUTPUT ACTIONS                               │ │
│  │                                                                         │ │
│  │  ⏭️ SKIP:     File is identical to source → No processing needed        │ │
│  │  📁 LOOSE:    File overrides source → Copy to loose files directory     │ │
│  │  📦 PACK:     File is new content → Copy to pack files directory       │ │
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
└─────────────────────────────────────────────────────────────┘
```

## 🎨 **Color-Coded Status Messages**

| Status | Color | Icon | Meaning | Action |
|--------|-------|------|---------|--------|
| `[MATCH FOUND]` | 🔍 Green | File exists in source directory | Proceed to hash check |
| `[NO MATCH]` | 📦 Blue | New file, safe to pack | Copy to pack directory |
| `[SKIP]` | ⏭️ Yellow | Identical file, no processing needed | Skip file entirely |
| `[OVERRIDE]` | 📁 Magenta | Modified file, must stay loose | Copy to loose directory |
| `[COPY FAIL]` | ❌ Red | Failed to copy file | Log error, continue |
| `[HASH FAIL]` | 💥 Red | Failed to calculate file hash | Log error, continue |
| `[EXCEPTION]` | ⚠️ Red | Unexpected error occurred | Log error, continue |

## 📊 **Real-World Example**

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

## 🎯 **Why This Matters**

- **SKIP files**: Save space and processing time
- **LOOSE files**: Preserve overrides for mod compatibility
- **PACK files**: Optimize for game performance
- **Error handling**: Ensures robust processing

*This intelligent classification is what makes Safe Resource Packer so powerful - it automatically makes the right decisions for every file!*
