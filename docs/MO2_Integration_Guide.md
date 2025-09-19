# 🎮 Mod Organizer 2 (MO2) Integration Guide

## 🎯 **Why MO2 Users Need Special Guidance**

Mod Organizer 2 uses a **Virtual File System (VFS)** that fundamentally changes how mods are managed compared to other mod managers. Our tool needs to work seamlessly with MO2's unique approach to mod isolation and profile management.

## 🏗️ **MO2's Virtual File System Explained**

### **How MO2 Works Differently:**

-   **Game Directory**: Stays completely clean and unmodified
-   **Mod Storage**: Each mod lives in its own isolated folder
-   **Virtual Merging**: MO2 creates a virtual view of all active mods
-   **Profile System**: Different mod setups without conflicts
-   **Load Order**: Precise control over which files override others

### **Why This Matters for Our Tool:**

-   Our packed files (BSA/BA2) need to be installed as **separate mods**
-   Our loose files need **higher priority** than packed files
-   MO2's conflict detection helps identify override issues
-   Profile management allows safe testing of packed mods

## 🚀 **Complete MO2 Workflow**

### **🎯 Choose Your Experience Level**

**🟢 Beginner (Simple & Safe):**

-   Install directly in your main MO2 profile
-   No need to create test profiles
-   Our tool is designed to be safe for your existing setup

**🔵 Advanced (Performance Testing):**

-   Create test profiles for A/B comparison
-   Compare original vs packed performance
-   Advanced troubleshooting and optimization

---

### **Step 1: Prepare Your Mod Collection**

```
MyModCollection/
├── ModA/
│   ├── ModA.esp
│   ├── meshes/
│   └── textures/
└── ModB/
    ├── ModB.esl
    └── scripts/
```

### **Step 2: Process with Safe Resource Packer**

```bash
# Use our batch repacker for MO2 collections
safe-resource-packer --batch-repack --collection ./MyModCollection \
                     --output ./MO2_Ready_Packages --game-type skyrim
```

**Result Structure:**

```
MO2_Ready_Packages/
├── ModA_Package/
│   ├── ModA_Packed.7z      # BSA + ESP
│   ├── ModA_Loose.7z       # Override files
│   └── Metadata/
└── ModB_Package/
    ├── ModB_Packed.7z
    ├── ModB_Loose.7z
    └── Metadata/
```

### **Step 3: Install in MO2**

**For Beginners**: Install directly in your main profile
**For Advanced Users**: Create a test profile first (see Advanced Features section)

### **Step 4: Install Packed Components**

#### **Install Packed Files (BSA + ESP):**

1. **Right-click in MO2** → **Install Mod**
2. **Select**: `ModA_Packed.7z`
3. **Name**: "ModA - Packed Assets"
4. **Enable the ESP** in MO2's plugin list
5. **Set Load Order**: Place after original mod ESPs

#### **Install Loose Files (Overrides):**

1. **Right-click in MO2** → **Install Mod**
2. **Select**: `ModA_Loose.7z`
3. **Name**: "ModA - Override Files"
4. **Set Priority**: **HIGHER** than packed files
5. **Verify**: Loose files override packed content

### **Step 5: Verify Installation**

#### **Check MO2's Data Tab:**

-   **Packed files**: Should show as BSA/BA2 archives
-   **Loose files**: Should show individual files
-   **Conflicts**: MO2 will highlight any conflicts

#### **Check Load Order:**

```
Original Mod ESPs
├── ModA.esp (original)
├── ModB.esl (original)
Packed Mod ESPs
├── ModA_Packed.esp (our generated)
├── ModB_Packed.esl (our generated)
```

## 🎯 **MO2-Specific Best Practices**

### **Profile Management:**

-   **Beginners**: Install directly in your main profile - it's safe!
-   **Advanced Users**: Create test profiles for A/B performance testing
-   **Use descriptive profile names**: "PackedMods_Test", "Performance_Optimized"

### **Load Order Strategy:**

```
1. Original mod ESPs (load first)
2. Packed mod ESPs (load after originals)
3. Loose override files (highest priority)
4. Patches and compatibility mods (load last)
```

### **Conflict Resolution:**

-   **MO2 will highlight conflicts** in red/yellow
-   **Loose files should always win** over packed files
-   **Use MO2's conflict resolution** to verify overrides work correctly

### **Performance Testing:**

-   **Compare loading times** between original and packed versions
-   **Monitor memory usage** during gameplay
-   **Test in different areas** to verify performance improvements

## 🛠️ **MO2 Troubleshooting**

### **Common Issues:**

#### **"Mod Not Loading"**

-   **Check**: ESP is enabled in MO2's plugin list
-   **Check**: BSA/BA2 is properly installed
-   **Check**: Load order is correct

#### **"Files Not Overriding"**

-   **Check**: Loose files have higher priority than packed files
-   **Check**: MO2's Data tab shows correct file hierarchy
-   **Check**: No conflicting mods with higher priority

#### **"Performance Issues"**

-   **Check**: BSA/BA2 archives are properly loaded
-   **Check**: No unnecessary loose files
-   **Check**: Archive invalidation is enabled

### **MO2-Specific Commands:**

```bash
# Check MO2's virtual file system
# (This is handled automatically by MO2)

# Verify mod installation
# Check MO2's Data tab for file conflicts

# Test performance
# Use MO2's built-in performance monitoring
```

## 📋 **MO2 Integration Checklist**

### **Before Processing:**

-   [ ] **Identify mods to pack**
-   [ ] **Note current load order** (optional)

### **During Processing:**

-   [ ] **Use batch repacker for collections**
-   [ ] **Verify output structure**
-   [ ] **Check for any errors**

### **After Processing:**

-   [ ] **Install packed files first**
-   [ ] **Install loose files with higher priority**
-   [ ] **Verify load order**
-   [ ] **Test in-game performance**
-   [ ] **Check for conflicts**

### **Performance Verification:**

-   [ ] **Compare loading times**
-   [ ] **Monitor memory usage**
-   [ ] **Test in different game areas**
-   [ ] **Verify no visual glitches**

## 🎮 **Advanced MO2 Features**

### **Profile Switching:**

-   **Quick testing**: Switch between original and packed profiles
-   **A/B comparison**: Compare performance side-by-side
-   **Safe rollback**: Return to original setup if needed

### **MO2 Tools Integration:**

-   **LOOT**: Automatic load order optimization
-   **Wrye Bash**: Bashed patch creation
-   **xEdit**: Conflict resolution and patching

### **Custom MO2 Workflows:**

-   **Automated installation**: Use MO2's command-line tools
-   **Batch operations**: Process multiple mods simultaneously
-   **Profile synchronization**: Keep multiple profiles in sync

## 🚀 **Next Steps**

1. **Test the workflow** with a small mod collection
2. **Create your first packed profile** in MO2
3. **Compare performance** between original and packed versions
4. **Share your results** with the community

---

_This guide is specifically designed for MO2 users who want to leverage our tool's power while maintaining MO2's advanced mod management capabilities._
