#!/usr/bin/env python3
"""
Complete Packaging Demo

Demonstrates the full end-to-end workflow:
1. Classification of files
2. Automatic BSA/BA2 creation
3. ESP generation
4. 7z compression
5. Final package assembly

This shows how Safe Resource Packer transforms from a simple classifier
into a complete mod distribution solution.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from safe_resource_packer import SafeResourcePacker
    from safe_resource_packer.packaging import PackageBuilder
    print("✅ Successfully imported Safe Resource Packer with packaging!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)


def create_demo_files():
    """Create demo files for the packaging demonstration."""
    print("🔧 Creating demo files...")

    # Create temporary directories
    base_dir = tempfile.mkdtemp(prefix="srp_packaging_demo_")
    source_dir = os.path.join(base_dir, "source")
    generated_dir = os.path.join(base_dir, "generated")

    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(generated_dir, exist_ok=True)

    # Create source files (these would be your original mod files)
    source_files = [
        "meshes/armor/steel/cuirass.nif",
        "meshes/armor/steel/boots.nif",
        "textures/armor/steel/cuirass_d.dds",
        "textures/armor/steel/boots_d.dds",
        "scripts/MyModScript.pex"
    ]

    for file_path in source_files:
        full_path = os.path.join(source_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            # Create dummy file content
            f.write(b"DUMMY_CONTENT_" + file_path.encode() + b"_" * 100)

    # Create generated files (these would be BodySlide output)
    generated_files = [
        # Files that match source (can be packed)
        "meshes/armor/steel/cuirass.nif",
        "meshes/armor/steel/boots.nif",

        # Files that don't match source (must stay loose)
        "meshes/actors/character/facegendata/facetint/MyMod.esp/00000001.dds",
        "textures/actors/character/overlays/custom_overlay.dds",

        # New files not in source (can be packed)
        "meshes/armor/custom/newpiece.nif",
        "textures/armor/custom/newpiece_d.dds"
    ]

    for file_path in generated_files:
        full_path = os.path.join(generated_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Make some files different from source to simulate BodySlide changes
        content = b"GENERATED_CONTENT_" + file_path.encode()
        if "cuirass" in file_path or "boots" in file_path:
            content += b"_MODIFIED_BY_BODYSLIDE" + b"_" * 200
        else:
            content += b"_NEW_FILE" + b"_" * 150

        with open(full_path, 'wb') as f:
            f.write(content)

    print(f"✅ Created demo files in: {base_dir}")
    print(f"   📁 Source files: {len(source_files)}")
    print(f"   📁 Generated files: {len(generated_files)}")

    return base_dir, source_dir, generated_dir


def create_demo_esp_template():
    """Create a simple ESP template for demonstration."""
    print("📄 Creating demo ESP template...")

    # Create a minimal ESP file (this is just for demo - real ESP would have proper headers)
    template_content = b"TES4\\x00\\x00\\x00\\x00" + b"\\x00" * 100  # Minimal ESP-like content

    template_dir = tempfile.mkdtemp(prefix="esp_template_")
    template_path = os.path.join(template_dir, "demo_template.esp")

    with open(template_path, 'wb') as f:
        f.write(template_content)

    print(f"✅ Created ESP template: {template_path}")
    return template_path


def demonstrate_complete_workflow():
    """Demonstrate the complete packaging workflow."""
    print("🚀 Starting Complete Packaging Demonstration")
    print("=" * 60)

    try:
        # Step 1: Create demo files
        base_dir, source_dir, generated_dir = create_demo_files()
        esp_template = create_demo_esp_template()

        # Step 2: Set up output directories
        pack_dir = os.path.join(base_dir, "pack")
        loose_dir = os.path.join(base_dir, "loose")
        package_dir = os.path.join(base_dir, "final_package")

        print("\n🧠 Step 1: File Classification")
        print("-" * 30)

        # Initialize the packer
        packer = SafeResourcePacker()

        # Process resources (classification)
        pack_count, loose_count, skip_count = packer.process_resources(
            source_dir, generated_dir, pack_dir, loose_dir
        )

        print(f"✅ Classification complete:")
        print(f"   📦 Pack files: {pack_count}")
        print(f"   📁 Loose files: {loose_count}")
        print(f"   ⏭️  Skipped files: {skip_count}")

        # Step 3: Complete packaging
        print("\n📦 Step 2: Complete Package Creation")
        print("-" * 30)

        # Prepare classification results for packaging
        classification_results = {}

        # Collect pack files
        if pack_count > 0 and os.path.exists(pack_dir):
            pack_files = []
            for root, dirs, files in os.walk(pack_dir):
                for file in files:
                    pack_files.append(os.path.join(root, file))
            classification_results['pack'] = pack_files
            print(f"📦 Found {len(pack_files)} files for BSA/BA2 creation")

        # Collect loose files
        if loose_count > 0 and os.path.exists(loose_dir):
            loose_files = []
            for root, dirs, files in os.walk(loose_dir):
                for file in files:
                    loose_files.append(os.path.join(root, file))
            classification_results['loose'] = loose_files
            print(f"📁 Found {len(loose_files)} files for loose archive")

        if classification_results:
            # Initialize package builder
            builder = PackageBuilder(
                game_type="skyrim",
                compression_level=5
            )

            # Add ESP template
            builder.add_esp_template(esp_template, "skyrim")

            # Build complete package
            mod_name = "AwesomeModDemo"
            options = {
                'cleanup_temp': False,  # Keep temp files for inspection
                'compression_level': 5
            }

            print(f"🔨 Building package '{mod_name}'...")
            success, package_path, package_info = builder.build_complete_package(
                classification_results, mod_name, package_dir, options
            )

            if success:
                print("\n🎉 PACKAGING SUCCESSFUL!")
                print("=" * 40)
                print(f"📦 Final Package: {package_path}")

                # Show package contents
                if package_info.get('components'):
                    print("\n📋 Package Contents:")
                    for comp_name, comp_info in package_info['components'].items():
                        comp_type = comp_name.replace('_', ' ').title()
                        size_mb = comp_info.get('info', {}).get('size_mb', 0)
                        file_count = comp_info.get('file_count', 'N/A')
                        print(f"   {comp_type}: {file_count} files ({size_mb:.1f} MB)")

                # Show what was created
                print("\n📁 Package Structure:")
                if os.path.exists(package_dir):
                    for root, dirs, files in os.walk(package_dir):
                        level = root.replace(package_dir, '').count(os.sep)
                        indent = ' ' * 2 * level
                        print(f"{indent}{os.path.basename(root)}/")
                        subindent = ' ' * 2 * (level + 1)
                        for file in files:
                            print(f"{subindent}{file}")

                # Show final package info
                if os.path.exists(package_path):
                    size_mb = os.path.getsize(package_path) / (1024 * 1024)
                    print(f"\n📦 Final package size: {size_mb:.1f} MB")

                print("\n🎯 What This Achieved:")
                print("✅ Classified files intelligently")
                print("✅ Created BSA/BA2 archive for optimal performance")
                print("✅ Generated ESP file to load the archive")
                print("✅ Compressed loose overrides separately")
                print("✅ Created final distribution package")
                print("✅ Generated installation instructions")
                print("✅ Provided complete metadata")

                print("\n🚀 Ready for Distribution!")
                print("This package can now be shared with users and installed like any professional mod.")

            else:
                print("❌ Package creation failed")
        else:
            print("⚠️  No files to package")

        # Cleanup
        print(f"\n🧹 Demo files created in: {base_dir}")
        print("You can inspect the results before cleanup.")

        return base_dir

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def show_cli_examples():
    """Show CLI command examples for the complete workflow."""
    print("\n" + "=" * 60)
    print("🖥️  CLI USAGE EXAMPLES")
    print("=" * 60)

    print("\n1️⃣  BASIC CLASSIFICATION (Current functionality):")
    print("safe-resource-packer --source ./Data --generated ./BodySlide_Output \\")
    print("                     --output-pack ./Pack --output-loose ./Loose")

    print("\n2️⃣  COMPLETE PACKAGING (New functionality):")
    print("safe-resource-packer --source ./Data --generated ./BodySlide_Output \\")
    print("                     --package ./MyMod_Package --mod-name \"MyAwesomeMod\" \\")
    print("                     --game-type skyrim --compression 7")

    print("\n3️⃣  WITH CUSTOM ESP TEMPLATE:")
    print("safe-resource-packer --source ./Data --generated ./BodySlide_Output \\")
    print("                     --package ./MyMod_Package --mod-name \"MyAwesomeMod\" \\")
    print("                     --esp-template ./my_template.esp --game-type fallout4")

    print("\n4️⃣  QUIET MODE FOR AUTOMATION:")
    print("safe-resource-packer --source ./Data --generated ./BodySlide_Output \\")
    print("                     --package ./MyMod_Package --mod-name \"MyAwesomeMod\" \\")
    print("                     --quiet --no-cleanup")

    print("\n🎯 The Result:")
    print("Instead of just getting classified files, you get:")
    print("✅ MyAwesomeMod_v1.0.7z - Complete, ready-to-share package")
    print("   ├── MyAwesomeMod.esp - ESP that loads the archive")
    print("   ├── MyAwesomeMod.bsa - Optimized game assets")
    print("   ├── MyAwesomeMod_Loose.7z - Override files")
    print("   └── Installation instructions + metadata")


if __name__ == "__main__":
    print("🧠 Safe Resource Packer - Complete Packaging Demo")
    print("This demonstrates the transformation from file classifier to complete mod packager!")
    print()

    # Run the demonstration
    demo_dir = demonstrate_complete_workflow()

    # Show CLI examples
    show_cli_examples()

    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("This tool now provides a complete end-to-end solution for mod creators!")
    print("From BodySlide output to professional mod packages in one command.")

    if demo_dir:
        print(f"\n📁 Demo files are in: {demo_dir}")
        print("Feel free to explore the generated package structure.")


