#!/usr/bin/env python3
"""
Enhanced CLI Demo - Showcases the beautiful CLI features
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from safe_resource_packer.enhanced_cli import EnhancedCLI
    from safe_resource_packer import SafeResourcePacker
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("❌ Enhanced CLI demo requires 'rich' library")
    print("Install with: pip install rich click colorama")
    sys.exit(1)


def create_demo_files():
    """Create demo files for testing."""
    console = Console()
    
    with console.status("[bold green]Creating demo files..."):
        # Create temporary directories
        demo_dir = Path(tempfile.mkdtemp(prefix="srp_demo_"))
        
        source_dir = demo_dir / "source"
        generated_dir = demo_dir / "generated"
        
        source_dir.mkdir(parents=True)
        generated_dir.mkdir(parents=True)
        
        # Create some demo files
        demo_files = {
            # Files that exist in both (will be skipped if identical)
            "meshes/armor/steel/cuirass.nif": "original steel cuirass mesh",
            "textures/armor/steel/cuirass.dds": "original steel cuirass texture",
            
            # Files that exist in both but are different (will go to loose)
            "meshes/actors/character/character.nif": "original character mesh",
            "textures/actors/character/skin.dds": "original skin texture",
        }
        
        # Create source files
        for file_path, content in demo_files.items():
            full_path = source_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Create generated files
        # Some identical files
        for file_path, content in list(demo_files.items())[:2]:
            full_path = generated_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)  # Same content - will be skipped
        
        # Some modified files
        for file_path, content in list(demo_files.items())[2:]:
            full_path = generated_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"MODIFIED: {content}")  # Different content - will go to loose
        
        # Some new files (will go to pack)
        new_files = {
            "meshes/armor/custom/newarmor.nif": "new custom armor mesh",
            "textures/armor/custom/newarmor.dds": "new custom armor texture",
            "meshes/weapons/custom/newsword.nif": "new custom sword mesh",
        }
        
        for file_path, content in new_files.items():
            full_path = generated_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    return demo_dir, source_dir, generated_dir


def demo_enhanced_features():
    """Demonstrate enhanced CLI features."""
    console = Console()
    cli = EnhancedCLI()
    
    # Show banner
    cli.print_banner()
    
    # Show help table
    console.print(Panel.fit("📋 Available CLI Options", border_style="blue"))
    cli.print_help_table()
    
    # Demo path validation
    console.print(Panel.fit("🔍 Path Validation Demo", border_style="yellow"))
    
    # Test with invalid path
    valid, message = cli.validate_path("/nonexistent/path", "demo")
    console.print(f"❌ Invalid path: [red]{message}[/red]")
    
    # Test with valid path
    valid, message = cli.validate_path(str(Path.cwd()), "demo")
    console.print(f"✅ Valid path: [green]{message}[/green]")
    
    # Demo file processing
    console.print(Panel.fit("🚀 Processing Demo", border_style="green"))
    
    # Create demo files
    demo_dir, source_dir, generated_dir = create_demo_files()
    
    try:
        pack_dir = demo_dir / "pack"
        loose_dir = demo_dir / "loose"
        pack_dir.mkdir()
        loose_dir.mkdir()
        
        # Create packer and process
        packer = SafeResourcePacker(threads=4, debug=False)
        
        # Demo progress with rich progress bar
        with cli.create_progress_bar("Demo Processing") as progress:
            task = progress.add_task("Processing files...", total=100)
            
            # Simulate processing steps
            import time
            for i in range(0, 101, 10):
                progress.update(task, advance=10)
                time.sleep(0.1)
        
        # Actually process the files
        console.print("\n🔄 Processing demo files...")
        pack_count, loose_count, skip_count = packer.process_resources(
            str(source_dir), str(generated_dir), str(pack_dir), str(loose_dir)
        )
        
        # Show beautiful summary
        import time
        cli.print_summary_table(pack_count, loose_count, skip_count, [], 2.5)
        cli.print_file_tree_summary(str(pack_dir), str(loose_dir))
        cli.print_next_steps(pack_count, loose_count)
        
    finally:
        # Cleanup demo files
        import shutil
        shutil.rmtree(demo_dir)
        console.print(f"\n🧹 Cleaned up demo files from: [dim]{demo_dir}[/dim]")


def demo_interactive_mode():
    """Demo the interactive mode (without actually running it)."""
    console = Console()
    
    console.print(Panel.fit(
        "🎮 Interactive Mode Demo\n\n"
        "The interactive mode provides:\n"
        "• 🔍 Automatic game detection\n"
        "• ✅ Path validation with suggestions\n"
        "• 🎯 Step-by-step configuration\n"
        "• 💡 Helpful hints and examples\n\n"
        "To try it: [cyan]safe-resource-packer --interactive[/cyan]",
        title="Interactive Mode Features",
        border_style="green"
    ))


def main():
    """Main demo function."""
    if not RICH_AVAILABLE:
        print("This demo requires the 'rich' library")
        return 1
    
    console = Console()
    
    console.print(Panel.fit(
        "🎨 Enhanced CLI Demo\n\n"
        "This demo showcases the beautiful and handy CLI features:",
        title="Safe Resource Packer - Enhanced CLI Demo",
        border_style="magenta"
    ))
    
    try:
        # Demo enhanced features
        demo_enhanced_features()
        
        # Demo interactive mode info
        demo_interactive_mode()
        
        console.print(Panel.fit(
            "✨ Enhanced CLI Features Summary:\n\n"
            "• 🎨 Beautiful colored output with Rich library\n"
            "• 📊 Progress bars with time estimates\n"
            "• 📋 Interactive mode for easy setup\n"
            "• ✅ Path validation with helpful suggestions\n"
            "• 📈 Beautiful summary tables and statistics\n"
            "• 🌳 File tree visualization\n"
            "• 🚀 Helpful next steps guidance\n"
            "• 🔍 Automatic game installation detection\n\n"
            "[bold green]Try it yourself:[/bold green]\n"
            "[cyan]safe-resource-packer --interactive[/cyan]\n"
            "[cyan]safe-resource-packer --help[/cyan]",
            title="🎉 Demo Complete!",
            border_style="green"
        ))
        
        return 0
        
    except Exception as e:
        console.print(f"[red]❌ Demo error: {e}[/red]")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
