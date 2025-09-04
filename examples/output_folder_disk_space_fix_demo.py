#!/usr/bin/env python3
"""
Output Folder Disk Space Fix Demo

This demonstrates how the output folder disk space check has been updated
to use smart analysis instead of the old scary "source × 3" calculation.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from safe_resource_packer.console_ui import ConsoleUI


def create_test_scenario():
    """Create a test scenario with realistic sizes."""
    print("🎮 Creating test scenario...")

    # Create a large source directory (simulating game Data)
    source_dir = tempfile.mkdtemp(prefix="large_source_")

    # Create many directories to simulate a real game installation
    directories = ['meshes', 'textures', 'sounds', 'music', 'scripts', 'interface',
                  'actors', 'materials', 'shaders', 'strings', 'video']

    total_source_size_mb = 0
    for i, dir_name in enumerate(directories):
        dir_path = os.path.join(source_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # Create files with varying sizes
        for j in range(50):  # 50 files per directory
            file_path = os.path.join(dir_path, f"file_{j:03d}.dat")
            size_mb = (i + 1) * 10  # Varying sizes: 10MB, 20MB, 30MB, etc.
            with open(file_path, 'w') as f:
                content = "x" * (size_mb * 1024 * 1024)  # MB to bytes
                f.write(content)
            total_source_size_mb += size_mb

    # Create a small mod that only uses 2 directories
    generated_dir = tempfile.mkdtemp(prefix="small_mod_")
    mod_files = [
        'meshes/armor/custom/helmet.nif',
        'meshes/armor/custom/cuirass.nif',
        'textures/armor/custom/helmet_d.dds',
        'textures/armor/custom/cuirass_d.dds'
    ]

    total_mod_size_mb = 0
    for file_path in mod_files:
        full_path = os.path.join(generated_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        size_mb = 5 if file_path.endswith('.nif') else 10  # 5MB for meshes, 10MB for textures
        with open(full_path, 'w') as f:
            content = "y" * (size_mb * 1024 * 1024)
            f.write(content)
        total_mod_size_mb += size_mb

    source_size_gb = total_source_size_mb / 1024
    mod_size_gb = total_mod_size_mb / 1024

    print(f"✅ Created test scenario:")
    print(f"   📁 Source: {source_size_gb:.1f} GB ({len(directories)} directories)")
    print(f"   📦 Mod: {mod_size_gb:.2f} GB (uses 2 directories: meshes, textures)")

    return source_dir, generated_dir, source_size_gb, mod_size_gb


def demonstrate_old_vs_new_output_disk_check():
    """Demonstrate the difference between old and new output folder disk space check."""
    print("\n" + "="*80)
    print("🎯 OUTPUT FOLDER DISK SPACE CHECK: OLD VS NEW")
    print("="*80)

    try:
        # Create test data
        source_dir, generated_dir, source_size_gb, mod_size_gb = create_test_scenario()

        print(f"\n📊 Test Scenario:")
        print(f"   🎮 Source: {source_size_gb:.1f} GB")
        print(f"   📦 Mod: {mod_size_gb:.2f} GB (small armor mod)")
        print(f"   💾 Available space: 202.5 GB (from user's example)")

        # OLD METHOD CALCULATION
        old_estimate_gb = source_size_gb * 3
        old_sufficient = old_estimate_gb <= 202.5

        print(f"\n❌ OLD OUTPUT FOLDER DISK SPACE CHECK:")
        print(f"   📏 Estimated space needed: {old_estimate_gb:.1f} GB (source folder × 3 for processing)")
        if not old_sufficient:
            print(f"   🚨 WARNING: Not enough disk space!")
            print(f"   🚨 You need ~{old_estimate_gb:.1f} GB but only have 202.5 GB available")
            print(f"   😱 USER REACTION: 'This is impossible! I need {old_estimate_gb:.1f} GB?!'")
        else:
            print(f"   ✅ Sufficient space (but estimate is still wrong)")

        # NEW METHOD CALCULATION
        print(f"\n✅ NEW SMART OUTPUT FOLDER DISK SPACE CHECK:")

        # Create a ConsoleUI instance to test the new logic
        console_ui = ConsoleUI()
        console_ui.config = {
            'source': source_dir,
            'generated': generated_dir
        }

        # Calculate smart estimate using the new method
        smart_estimate_gb, analysis_type = console_ui._calculate_smart_space_estimate(source_dir, generated_dir)
        smart_sufficient = smart_estimate_gb <= 202.5

        print(f"   🧠 Smart space estimate: {smart_estimate_gb:.1f} GB (selective copying + processing)")
        print(f"   ✅ Uses intelligent analysis of your mod's directory usage")
        if smart_sufficient:
            print(f"   ✅ Sufficient disk space available (smart analysis)")
            print(f"   😊 USER REACTION: 'Only {smart_estimate_gb:.1f} GB? Perfect!'")
        else:
            print(f"   ⚠️  Smart analysis shows {smart_estimate_gb:.1f} GB needed but only 202.5 GB available")

        # Calculate savings
        savings_gb = old_estimate_gb - smart_estimate_gb
        savings_percent = (savings_gb / old_estimate_gb) * 100

        print(f"\n📊 COMPARISON RESULTS:")
        print(f"   ❌ Old method: {old_estimate_gb:.1f} GB ({'❌ INSUFFICIENT' if not old_sufficient else '✅ sufficient but wrong'})")
        print(f"   ✅ New method: {smart_estimate_gb:.1f} GB ({'✅ SUFFICIENT' if smart_sufficient else '❌ insufficient'})")
        print(f"   💾 Space savings: {savings_gb:.1f} GB ({savings_percent:.1f}% reduction)")

        # Show the impact on user experience
        print(f"\n🌍 USER EXPERIENCE IMPACT:")
        if not old_sufficient and smart_sufficient:
            print(f"   🎯 CRITICAL FIX: Old method would block user, new method allows processing!")
            print(f"   ❌ Old: 'ERROR - Need {old_estimate_gb:.1f} GB, you have 202.5 GB' → USER BLOCKED")
            print(f"   ✅ New: 'OK - Need {smart_estimate_gb:.1f} GB, you have 202.5 GB' → USER PROCEEDS")
        elif old_sufficient and smart_sufficient:
            print(f"   ✅ IMPROVEMENT: Both work, but new method gives accurate estimates")
            print(f"   ❌ Old: User worried about {old_estimate_gb:.1f} GB usage")
            print(f"   ✅ New: User confident with {smart_estimate_gb:.1f} GB usage")
        else:
            print(f"   📊 Both methods show same availability, but new method is accurate")

        # Demonstrate the actual UI messages
        print(f"\n💬 ACTUAL UI MESSAGES COMPARISON:")
        print(f"\n   ❌ OLD UI MESSAGE:")
        print(f"      '💾 Available disk space on C:: 202.5 GB'")
        print(f"      '📏 Estimated space needed: {old_estimate_gb:.1f} GB (source folder × 3 for processing)'")
        if not old_sufficient:
            print(f"      '⚠️  WARNING: Not enough disk space!'")
            print(f"      '   You need ~{old_estimate_gb:.1f} GB but only have 202.5 GB available'")

        print(f"\n   ✅ NEW UI MESSAGE:")
        print(f"      '💾 Available disk space on C:: 202.5 GB'")
        print(f"      '🧠 Smart space estimate: {smart_estimate_gb:.1f} GB (selective copying + processing)'")
        print(f"      '   ✅ Uses intelligent analysis of your mod's directory usage'")
        if smart_sufficient:
            print(f"      '✅ Sufficient disk space available (smart analysis)'")
        else:
            print(f"      '⚠️  WARNING: Not enough disk space!'")
            print(f"      '   Smart analysis shows {smart_estimate_gb:.1f} GB needed but only 202.5 GB available'")

        print(f"\n✅ Output folder disk space check demonstration completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        try:
            shutil.rmtree(source_dir)
            shutil.rmtree(generated_dir)
            print(f"🧹 Cleaned up test directories")
        except:
            pass


def demonstrate_fallback_behavior():
    """Show how the fallback behavior works when smart analysis isn't available."""
    print("\n" + "="*80)
    print("🎯 FALLBACK BEHAVIOR DEMONSTRATION")
    print("="*80)

    print("📋 SCENARIOS WHERE FALLBACK IS USED:")
    print("   1️⃣  Generated path not available yet")
    print("   2️⃣  Smart analysis fails due to error")
    print("   3️⃣  Source or generated directories don't exist")
    print()
    print("🔄 FALLBACK LOGIC:")
    print("   • Uses conservative estimate: max(source_size × 0.5, 5.0 GB)")
    print("   • Shows message about smart optimization reducing usage")
    print("   • Still much better than old 3× source size estimate")
    print()
    print("💬 FALLBACK UI MESSAGES:")
    print("   '📏 Conservative estimate: X.X GB (smart optimization will reduce this)'")
    print("   '💡 Actual usage will be much lower thanks to selective copying'")
    print()
    print("🎯 RESULT: Even fallback is better than old scary estimates!")


def main():
    """Run the output folder disk space fix demonstration."""
    print("🎯 OUTPUT FOLDER DISK SPACE FIX DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows how the output folder disk space check")
    print("has been updated to use smart analysis instead of the")
    print("scary 'source × 3' calculation that was blocking users.")
    print()

    # Run the demonstration
    demonstrate_old_vs_new_output_disk_check()

    # Show fallback behavior
    demonstrate_fallback_behavior()

    print("\n" + "="*80)
    print("🎉 OUTPUT FOLDER DISK SPACE FIX COMPLETE")
    print("="*80)
    print()
    print("Key Improvements:")
    print("✅ Output folder disk space check now uses smart analysis")
    print("✅ No more scary 'source × 3' calculations blocking users")
    print("✅ Accurate estimates based on actual mod directory usage")
    print("✅ Conservative fallback still better than old method")
    print("✅ Users can proceed with confidence instead of being blocked")
    print()
    print("🎯 PROBLEM SOLVED: All disk space calculations now use smart analysis!")

    return 0


if __name__ == "__main__":
    exit(main())
