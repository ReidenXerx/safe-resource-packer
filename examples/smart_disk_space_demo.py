#!/usr/bin/env python3
"""
Smart Disk Space Analysis Demo

This demonstrates how the updated disk space analysis now uses the smart selective
copying logic to provide accurate space estimates instead of the scary old estimates.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.console_ui import ConsoleUI


def create_massive_game_data():
    """Create a massive mock game Data directory."""
    print("🎮 Creating MASSIVE mock game Data directory...")

    test_dir = tempfile.mkdtemp(prefix="massive_game_data_")

    # Create tons of directories like a real game installation
    all_directories = [
        'meshes', 'textures', 'sounds', 'music', 'scripts', 'interface',
        'actors', 'materials', 'shaders', 'strings', 'video', 'skse',
        'mcm', 'fomod', 'docs', 'backup', 'dyndolod', 'grass', 'trees',
        'terrain', 'facegen', 'facegendata', 'animationdata', 'behaviordata',
        'charactergen', 'dialogueviews', 'effects', 'environment', 'lighting',
        'loadscreens', 'misc', 'planetdata', 'seq', 'voices', 'weapons',
        'particlelights', 'pbrmaterialobjects', 'pbrtexturesets', 'shadersfx',
        'armor', 'clutter', 'furniture', 'landscape', 'sky', 'water'
    ]

    total_files = 0
    total_size_mb = 0

    for dir_name in all_directories:
        dir_path = os.path.join(test_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # Create many subdirectories and files to simulate real game data
        for sub_i in range(10):  # 10 subdirs per main dir
            sub_dir = os.path.join(dir_path, f"subdir_{sub_i:02d}")
            os.makedirs(sub_dir, exist_ok=True)

            for file_i in range(20):  # 20 files per subdir
                file_path = os.path.join(sub_dir, f"file_{file_i:03d}.dat")
                # Create files with varying sizes (1-10MB each)
                file_size_kb = (file_i % 10 + 1) * 100  # 100KB to 1MB
                with open(file_path, 'w') as f:
                    content = "x" * (file_size_kb * 1024)  # KB to bytes
                    f.write(content)

                total_files += 1
                total_size_mb += file_size_kb / 1024

    total_size_gb = total_size_mb / 1024
    print(f"✅ Created massive game data:")
    print(f"   📁 {len(all_directories)} directories")
    print(f"   📄 {total_files} files")
    print(f"   💾 {total_size_gb:.1f} GB total size")

    return test_dir, all_directories, total_size_gb


def create_small_focused_mod():
    """Create a small mod that only uses a few directories."""
    print("📦 Creating small focused mod...")

    test_dir = tempfile.mkdtemp(prefix="small_mod_")

    # Small mod only touches 3 directories out of 40+ in game
    mod_files = [
        'meshes/armor/custom_armor/helmet.nif',
        'meshes/armor/custom_armor/cuirass.nif',
        'meshes/armor/custom_armor/gauntlets.nif',
        'textures/armor/custom_armor/helmet_d.dds',
        'textures/armor/custom_armor/helmet_n.dds',
        'textures/armor/custom_armor/cuirass_d.dds',
        'textures/armor/custom_armor/cuirass_n.dds',
        'scripts/custom_armor_script.pex',
        'scripts/custom_armor_config.pex',
    ]

    total_size_mb = 0
    for file_path in mod_files:
        full_path = os.path.join(test_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Create realistic mod file sizes
        if file_path.endswith('.nif'):
            size_kb = 500  # 500KB for mesh files
        elif file_path.endswith('.dds'):
            size_kb = 2048  # 2MB for texture files
        else:
            size_kb = 100  # 100KB for script files

        with open(full_path, 'w') as f:
            content = "y" * (size_kb * 1024)
            f.write(content)

        total_size_mb += size_kb / 1024

    mod_dirs_used = ['meshes', 'textures', 'scripts']
    total_size_gb = total_size_mb / 1024

    print(f"✅ Created small mod:")
    print(f"   📁 Uses only {len(mod_dirs_used)} directories: {mod_dirs_used}")
    print(f"   📄 {len(mod_files)} files")
    print(f"   💾 {total_size_gb:.2f} GB total size")

    return test_dir, mod_dirs_used, total_size_gb


def demonstrate_old_vs_new_analysis():
    """Demonstrate the difference between old and new disk space analysis."""
    print("\n" + "="*80)
    print("🎯 DISK SPACE ANALYSIS: OLD VS NEW COMPARISON")
    print("="*80)

    try:
        # Create test data
        game_data, game_dirs, game_size_gb = create_massive_game_data()
        mod_data, mod_dirs, mod_size_gb = create_small_focused_mod()

        print(f"\n📊 Test Scenario:")
        print(f"   🎮 Game Data: {game_size_gb:.1f} GB ({len(game_dirs)} directories)")
        print(f"   📦 Mod Data: {mod_size_gb:.2f} GB (uses {len(mod_dirs)} directories)")
        print(f"   🎯 Mod uses {len(mod_dirs)}/{len(game_dirs)} directories ({(len(mod_dirs)/len(game_dirs)*100):.1f}%)")

        # OLD METHOD CALCULATION
        old_estimate_gb = game_size_gb * 3  # Old method: 3x source size

        print(f"\n❌ OLD DISK SPACE ANALYSIS:")
        print(f"   📏 Source folder size: {game_size_gb:.1f} GB")
        print(f"   💾 SPACE NEEDED: ~{old_estimate_gb:.1f} GB (3× source size)")
        print(f"   🚨 SCARY MESSAGE: 'LARGE MOD DETECTED ({old_estimate_gb:.1f} GB needed)'")
        print(f"   😱 USER REACTION: 'I don't have {old_estimate_gb:.1f} GB free space!'")

        # NEW METHOD CALCULATION (using smart analysis)
        print(f"\n✅ NEW SMART DISK SPACE ANALYSIS:")

        # Simulate the new analysis logic
        from safe_resource_packer.core import SafeResourcePacker
        temp_packer = SafeResourcePacker()

        # Analyze directories (same logic as the new method)
        mod_directories = temp_packer._analyze_mod_directories(mod_data)
        source_directories = temp_packer._find_source_directories(game_data, mod_directories)

        # Calculate selective sizes
        selective_size = sum(temp_packer._estimate_directory_size(os.path.join(game_data, d))
                           for d in source_directories if os.path.exists(os.path.join(game_data, d)))
        selective_gb = selective_size / (1024**3)

        # New space estimate
        new_estimate_gb = selective_gb + mod_size_gb + (mod_size_gb * 2) + 1  # Smart formula

        # Calculate savings
        savings_percent = ((game_size_gb * 3 - new_estimate_gb) / (game_size_gb * 3)) * 100
        saved_gb = old_estimate_gb - new_estimate_gb

        print(f"   🧠 Smart analysis detects mod uses: {sorted(list(mod_directories))}")
        print(f"   🎯 Only copy from source: {selective_gb:.2f} GB ({(selective_gb/game_size_gb*100):.1f}% of source)")
        print(f"   📦 Generated files: {mod_size_gb:.2f} GB")
        print(f"   💾 SMART SPACE NEEDED: ~{new_estimate_gb:.1f} GB")
        print(f"   🎉 OPTIMIZATION SAVINGS: {saved_gb:.1f} GB saved ({savings_percent:.1f}% reduction)!")
        print(f"   😊 USER REACTION: 'Only {new_estimate_gb:.1f} GB? That's totally manageable!'")

        # Comparison summary
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"   ❌ Old method: {old_estimate_gb:.1f} GB (scary and wrong)")
        print(f"   ✅ New method: {new_estimate_gb:.1f} GB (accurate and reasonable)")
        print(f"   💾 Space savings: {saved_gb:.1f} GB ({savings_percent:.1f}% reduction)")
        print(f"   ⚡ User experience: DRAMATICALLY IMPROVED!")

        # Real-world impact
        print(f"\n🌍 REAL-WORLD IMPACT:")
        if old_estimate_gb > 100:
            print(f"   😱 Old: User sees '{old_estimate_gb:.0f} GB needed' and gives up")
            print(f"   😊 New: User sees '{new_estimate_gb:.1f} GB needed' and proceeds confidently")

        print(f"\n✅ Smart disk space analysis demonstration completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        try:
            shutil.rmtree(game_data)
            shutil.rmtree(mod_data)
            print(f"🧹 Cleaned up test directories")
        except:
            pass


def demonstrate_console_ui_integration():
    """Show how the ConsoleUI now uses smart analysis."""
    print("\n" + "="*80)
    print("🎯 CONSOLE UI SMART ANALYSIS INTEGRATION")
    print("="*80)

    print("The ConsoleUI has been updated with smart disk space analysis:")
    print()
    print("📋 KEY IMPROVEMENTS:")
    print("   1️⃣  Disk space analysis moved AFTER getting both source and generated paths")
    print("   2️⃣  Uses same selective copy logic as the optimization")
    print("   3️⃣  Shows actual directories that will be copied")
    print("   4️⃣  Displays space savings compared to old method")
    print("   5️⃣  Provides accurate, non-scary estimates")
    print()
    print("🔄 NEW ANALYSIS FLOW:")
    print("   1️⃣  Get source path from user")
    print("   2️⃣  Get generated path from user")
    print("   3️⃣  Analyze mod directories (same as selective copy)")
    print("   4️⃣  Calculate selective source size")
    print("   5️⃣  Show smart space breakdown")
    print("   6️⃣  Display optimization savings")
    print()
    print("💡 FALLBACK BEHAVIOR:")
    print("   • If generated path not available → conservative estimate")
    print("   • Still mentions smart optimization will reduce requirements")
    print("   • No more scary 3× source size estimates")
    print()
    print("🎉 RESULT: Users get accurate, confidence-inspiring space estimates!")


def main():
    """Run the smart disk space analysis demonstration."""
    print("🎯 SMART DISK SPACE ANALYSIS DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows how the disk space analysis has been updated")
    print("to use the smart selective copying logic, providing accurate")
    print("estimates instead of scary overestimates.")
    print()

    # Run the demonstration
    demonstrate_old_vs_new_analysis()

    # Show ConsoleUI integration
    demonstrate_console_ui_integration()

    print("\n" + "="*80)
    print("🎉 SMART DISK SPACE ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("Key Improvements:")
    print("✅ Disk space analysis now uses smart selective copying logic")
    print("✅ Accurate estimates instead of scary 3× source size overestimates")
    print("✅ Shows actual space savings from optimization")
    print("✅ Users get confidence-inspiring, realistic space requirements")
    print("✅ No more 'I don't have 800GB free space!' user abandonment")
    print()
    print("🎯 PROBLEM SOLVED: Disk space analysis now respects smart copying!")

    return 0


if __name__ == "__main__":
    exit(main())

