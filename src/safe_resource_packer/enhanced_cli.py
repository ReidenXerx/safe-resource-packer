"""
Enhanced CLI interface with beautiful colors, progress bars, and interactive features.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import click
    from rich.console import Console
    from rich.progress import (
        Progress, SpinnerColumn, TextColumn, BarColumn,
        TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    click = None

from .core import SafeResourcePacker
from .utils import log, write_log_file, set_debug, get_skipped
from .clean_output import CleanOutputManager, create_clean_progress_callback, enhance_classifier_output
from .packaging import PackageBuilder


class EnhancedCLI:
    """Enhanced CLI with beautiful output and interactive features."""

    def __init__(self):
        """Initialize the enhanced CLI."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        self.packer = None

    def print_banner(self):
        """Print a beautiful banner."""
        if not RICH_AVAILABLE:
            print("🧠 Safe Resource Packer v1.0.0")
            print("Intelligent file classification for game modding")
            print("=" * 50)
            return

        banner = Text("Safe Resource Packer", style="bold blue")
        subtitle = Text("Intelligent file classification for game modding", style="italic cyan")
        philosophy = Text("🎯 Solves: Performance issues from loose files in big modlists\n📦 Method: Smart classification of generated assets (BodySlide, etc.)\n🚀 Result: 3x faster loading, smooth gameplay", style="dim white")

        panel = Panel.fit(
            f"{banner}\n{subtitle}\n\n{philosophy}\n\nVersion 1.0.0 | Author: Dudu",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(panel)
        self.console.print()

    def print_help_table(self):
        """Print a beautiful help table."""
        if not RICH_AVAILABLE:
            print("Available commands:")
            print("  --interactive    Interactive mode")
            print("  --validate       Validate paths only")
            print("  --help          Show help")
            return

        table = Table(title="Available Options", box=box.ROUNDED)
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Default", style="yellow")

        table.add_row("--source", "Path to reference files (e.g., Skyrim Data)", "[red]Required[/red]")
        table.add_row("--generated", "Path to generated files (e.g., BodySlide output)", "[red]Required[/red]")
        table.add_row("--output-pack", "Directory for packable files", "[red]Required[/red]")
        table.add_row("--output-loose", "Directory for loose files", "[red]Required[/red]")
        table.add_row("--threads", "Number of processing threads", "8")
        table.add_row("--debug", "Enable detailed logging", "False")
        table.add_row("--interactive", "Interactive mode", "False")
        table.add_row("--validate", "Validate paths only", "False")
        table.add_row("--quiet", "Quiet mode (minimal output)", "False")
        table.add_row("--clean", "Clean output (less verbose)", "False")
        table.add_row("--philosophy", "Show philosophy and purpose", "False")

        # Packaging options
        table.add_row("", "", "")  # Separator
        table.add_row("[bold]PACKAGING OPTIONS[/bold]", "", "")
        table.add_row("--package", "Create complete mod package at this path", "None")
        table.add_row("--mod-name", "Name for the mod package", "Auto-detect")
        table.add_row("--game-type", "Target game (skyrim or fallout4)", "skyrim")
        table.add_row("--game-path", "Game installation path for bulletproof detection", "None")
        table.add_row("--esp-template", "Path to ESP template file", "None")
        table.add_row("--compression", "7z compression level (0-9)", "5")
        table.add_row("--no-cleanup", "Keep temporary packaging files", "False")
        table.add_row("--install-bsarch", "Install BSArch for optimal BSA/BA2 creation", "False")

        self.console.print(table)
        self.console.print()

    def validate_path(self, path: str, path_type: str) -> Tuple[bool, str]:
        """Validate a path and provide helpful feedback."""
        if not path:
            return False, f"{path_type} path cannot be empty"

        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            # Check for common mistakes
            suggestions = []
            parent = path_obj.parent
            if parent.exists():
                # Look for similar directories
                similar = [d for d in parent.iterdir()
                          if d.is_dir() and d.name.lower().startswith(path_obj.name.lower()[:3])]
                if similar:
                    suggestions.append(f"Did you mean: {', '.join(str(s) for s in similar[:3])}")

            suggestion_text = f" {suggestions[0]}" if suggestions else ""
            return False, f"{path_type} path does not exist: {path}{suggestion_text}"

        if path_type in ["source", "generated"] and not path_obj.is_dir():
            return False, f"{path_type} path must be a directory: {path}"

        return True, f"✓ {path_type} path is valid"

    def interactive_mode(self) -> dict:
        """Interactive mode for easier parameter selection."""
        if not RICH_AVAILABLE:
            print("\nInteractive mode requires 'rich' library. Install with: pip install rich")
            return {}

        self.console.print(Panel.fit(
            "🎮 Interactive Setup Mode\n\nI'll help you configure the Safe Resource Packer step by step.",
            title="Interactive Mode",
            border_style="green"
        ))

        config = {}

        # Detect common game installations
        common_paths = self._detect_common_paths()
        if common_paths:
            self.console.print("\n🔍 Detected potential game installations:")
            for i, (game, path) in enumerate(common_paths.items(), 1):
                self.console.print(f"  {i}. {game}: [cyan]{path}[/cyan]")

        # Source path
        while True:
            if common_paths:
                choice = Prompt.ask(
                    "\n📁 Select source directory",
                    choices=[str(i) for i in range(1, len(common_paths) + 1)] + ["custom"],
                    default="custom"
                )

                if choice != "custom":
                    config['source'] = list(common_paths.values())[int(choice) - 1]
                    break

            source = Prompt.ask("📁 Enter source directory path (e.g., Skyrim Data folder)")
            valid, message = self.validate_path(source, "source")

            if valid:
                config['source'] = source
                self.console.print(f"[green]{message}[/green]")
                break
            else:
                self.console.print(f"[red]❌ {message}[/red]")

        # Generated path
        while True:
            generated = Prompt.ask("🔧 Enter generated files directory (e.g., BodySlide output)")
            valid, message = self.validate_path(generated, "generated")

            if valid:
                config['generated'] = generated
                self.console.print(f"[green]{message}[/green]")
                break
            else:
                self.console.print(f"[red]❌ {message}[/red]")

        # Output directories
        config['output_pack'] = Prompt.ask("📦 Enter pack output directory", default="./pack")
        config['output_loose'] = Prompt.ask("📁 Enter loose output directory", default="./loose")

        # Advanced options
        if Confirm.ask("⚙️ Configure advanced options?", default=False):
            config['threads'] = int(Prompt.ask("🧵 Number of threads", default="8"))
            config['debug'] = Confirm.ask("🐛 Enable debug mode?", default=False)
        else:
            config['threads'] = 8
            config['debug'] = False

        config['log'] = Prompt.ask("📋 Log file path", default="safe_resource_packer.log")

        return config

    def _detect_common_paths(self) -> dict:
        """Detect common game installation paths."""
        common_paths = {}

        # Windows paths
        if sys.platform == "win32":
            possible_paths = [
                ("Skyrim SE", "C:/Program Files (x86)/Steam/steamapps/common/Skyrim Special Edition/Data"),
                ("Skyrim LE", "C:/Program Files (x86)/Steam/steamapps/common/Skyrim/Data"),
                ("Fallout 4", "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4/Data"),
                ("Fallout NV", "C:/Program Files (x86)/Steam/steamapps/common/Fallout New Vegas/Data"),
            ]
        else:
            # Linux Steam paths
            home = Path.home()
            possible_paths = [
                ("Skyrim SE", home / ".steam/steam/steamapps/common/Skyrim Special Edition/Data"),
                ("Fallout 4", home / ".steam/steam/steamapps/common/Fallout 4/Data"),
            ]

        for game, path in possible_paths:
            if Path(path).exists():
                common_paths[game] = str(path)

        return common_paths

    def create_progress_bar(self, description: str = "Processing"):
        """Create a beautiful progress bar."""
        if not RICH_AVAILABLE:
            return None

        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )

    def print_summary_table(self, pack_count: int, loose_count: int, skip_count: int,
                          skipped_files: list, processing_time: float):
        """Print a beautiful summary table."""
        if not RICH_AVAILABLE:
            print(f"\n===== SUMMARY =====")
            print(f"Pack files: {pack_count}")
            print(f"Loose files: {loose_count}")
            print(f"Skipped files: {skip_count}")
            print(f"Errors: {len(skipped_files)}")
            print(f"Processing time: {processing_time:.2f}s")
            return

        # Main summary table
        table = Table(title="📊 Processing Summary", box=box.ROUNDED)
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Count", style="yellow", justify="right")
        table.add_column("Description", style="white")

        table.add_row(
            "📦 Pack Files",
            str(pack_count),
            "[green]Safe to pack into BSA/BA2 archives[/green]"
        )
        table.add_row(
            "📁 Loose Files",
            str(loose_count),
            "[yellow]Should remain as loose files (overrides)[/yellow]"
        )
        table.add_row(
            "⏭️  Skipped",
            str(skip_count),
            "[blue]Identical files (no processing needed)[/blue]"
        )
        table.add_row(
            "❌ Errors",
            str(len(skipped_files)),
            "[red]Files that couldn't be processed[/red]"
        )

        self.console.print(table)

        # Performance info
        perf_panel = Panel(
            f"⏱️  Processing time: [yellow]{processing_time:.2f}s[/yellow]\n"
            f"🧵 Threads used: [cyan]{self.packer.threads if self.packer else 'N/A'}[/cyan]\n"
            f"📈 Files/second: [green]{(pack_count + loose_count + skip_count) / max(processing_time, 0.1):.1f}[/green]",
            title="Performance",
            border_style="blue"
        )
        self.console.print(perf_panel)

    def print_file_tree_summary(self, output_pack: str, output_loose: str):
        """Print a file tree summary of outputs."""
        if not RICH_AVAILABLE:
            return

        tree = Tree("📁 Output Structure")

        pack_branch = tree.add(f"📦 [cyan]{output_pack}[/cyan] (Pack Directory)")
        loose_branch = tree.add(f"📁 [yellow]{output_loose}[/yellow] (Loose Directory)")

        # Show some sample files if directories exist
        pack_path = Path(output_pack)
        if pack_path.exists():
            files = list(pack_path.rglob("*"))[:5]
            for file in files:
                if file.is_file():
                    pack_branch.add(f"📄 {file.relative_to(pack_path)}")
            if len(list(pack_path.rglob("*"))) > 5:
                pack_branch.add("📄 ... and more")

        loose_path = Path(output_loose)
        if loose_path.exists():
            files = list(loose_path.rglob("*"))[:5]
            for file in files:
                if file.is_file():
                    loose_branch.add(f"📄 {file.relative_to(loose_path)}")
            if len(list(loose_path.rglob("*"))) > 5:
                loose_branch.add("📄 ... and more")

        self.console.print(tree)

    def show_philosophy(self):
        """Show the philosophy and purpose of the tool."""
        if not RICH_AVAILABLE:
            print("🧠 Safe Resource Packer - Philosophy & Purpose")
            print("=" * 50)
            print()
            print("THE PROBLEM:")
            print("Big modlists suffer from performance issues due to thousands of loose files.")
            print("The Creation Engine handles loose files poorly, causing:")
            print("- Slow loading times (3x slower)")
            print("- Memory fragmentation")
            print("- Stuttering gameplay")
            print("- Especially bad on Proton/Linux (10x slower)")
            print()
            print("THE SOLUTION:")
            print("Smart classification of generated files into three categories:")
            print("📦 Pack Files - New content safe to pack into BSA/BA2")
            print("📁 Loose Files - Critical overrides that must stay loose")
            print("⏭️ Skip Files - Identical copies that can be deleted")
            print()
            print("THE RESULT:")
            print("🚀 3x faster loading times")
            print("🎮 Smooth, stutter-free gameplay")
            print("💾 Optimized memory usage")
            print("🛡️ No broken mods or missing assets")
            print()
            print("For full details, see: PHILOSOPHY.md")
            return

        # Rich version
        self.console.print(Panel.fit(
            "[bold blue]🧠 Safe Resource Packer - Philosophy & Purpose[/bold blue]\n\n"
            "[yellow]THE PROBLEM WE SOLVE:[/yellow]\n"
            "Big modlists create performance nightmares with thousands of loose files.\n"
            "The Creation Engine treats loose files terribly, causing:\n\n"
            "• [red]Slow loading[/red] - 3x longer load times\n"
            "• [red]Memory waste[/red] - Fragmented memory usage\n"
            "• [red]Stuttering[/red] - Poor gameplay experience\n"
            "• [red]Proton pain[/red] - 10x worse on Steam Deck/Linux\n\n"
            "[green]OUR SMART SOLUTION:[/green]\n"
            "Intelligent classification of generated files:\n\n"
            "📦 [blue]Pack Files[/blue] - New content safe for BSA/BA2 archives\n"
            "📁 [magenta]Loose Files[/magenta] - Critical overrides that must stay loose\n"
            "⏭️ [yellow]Skip Files[/yellow] - Identical copies that waste space\n\n"
            "[cyan]THE AMAZING RESULTS:[/cyan]\n"
            "🚀 [green]3x faster loading times[/green]\n"
            "🎮 [green]Smooth, stutter-free gameplay[/green]\n"
            "💾 [green]Optimized memory usage[/green]\n"
            "🛡️ [green]Zero broken mods or missing assets[/green]\n\n"
            "[dim]For complete technical details and examples, see: PHILOSOPHY.md[/dim]",
            title="Why This Tool Exists",
            border_style="blue",
            padding=(1, 2)
        ))

    def print_next_steps(self, pack_count: int, loose_count: int):
        """Print helpful next steps."""
        if not RICH_AVAILABLE:
            print("\nNext steps:")
            if pack_count > 0:
                print("1. Pack the files in the pack directory into BSA/BA2")
            if loose_count > 0:
                print("2. Keep loose files as-is in your mod manager")
            return

        steps = []

        if pack_count > 0:
            steps.append("1. 📦 Create BSA/BA2 archive from pack directory files")
            steps.append("   Use tools like BSArch, Cathedral Assets Optimizer, or Creation Kit")

        if loose_count > 0:
            steps.append("2. 📁 Deploy loose files to your mod manager")
            steps.append("   These files override existing content and should stay loose")

        steps.append("3. 🎮 Test your mod setup in-game")
        steps.append("4. 📋 Check the log file for any errors or warnings")

        if steps:
            next_steps = Panel(
                "\n".join(steps),
                title="🚀 Next Steps",
                border_style="green"
            )
            self.console.print(next_steps)

    def _handle_packaging(self, args, pack_count: int, loose_count: int, quiet_mode: bool) -> dict:
        """Handle the complete packaging process."""
        try:
            # Determine mod name
            mod_name = args.mod_name
            if not mod_name:
                if args.generated:
                    mod_name = os.path.basename(os.path.normpath(args.generated))
                else:
                    mod_name = "ModPackage"

            # Show packaging start
            if not quiet_mode and RICH_AVAILABLE:
                self.console.print(f"\n[bold blue]📦 Starting package creation for '{mod_name}'...[/bold blue]")
            else:
                print(f"\n📦 Creating package for '{mod_name}'...")

            # Prepare classification results
            classification_results = {}

            # Collect pack files
            if pack_count > 0 and args.output_pack and os.path.exists(args.output_pack):
                pack_files = []
                for root, dirs, files in os.walk(args.output_pack):
                    for file in files:
                        pack_files.append(os.path.join(root, file))
                classification_results['pack'] = pack_files

            # Collect loose files
            if loose_count > 0 and args.output_loose and os.path.exists(args.output_loose):
                loose_files = []
                for root, dirs, files in os.walk(args.output_loose):
                    for file in files:
                        loose_files.append(os.path.join(root, file))
                classification_results['loose'] = loose_files

            if not classification_results:
                if not quiet_mode:
                    self.console.print("[yellow]⚠️  No files to package[/yellow]")
                else:
                    print("⚠️  No files to package")
                return {'success': False, 'message': 'No files to package'}

            # Set up packaging options
            options = {
                'cleanup_temp': not args.no_cleanup,
                'compression_level': args.compression
            }

            # Initialize package builder
            builder = PackageBuilder(
                game_type=args.game_type,
                compression_level=args.compression
            )

            # Add ESP template if provided
            if args.esp_template:
                if os.path.exists(args.esp_template):
                    builder.add_esp_template(args.esp_template, args.game_type)
                    if not quiet_mode:
                        self.console.print(f"[green]✅ Added ESP template: {args.esp_template}[/green]")
                else:
                    if not quiet_mode:
                        self.console.print(f"[yellow]⚠️  ESP template not found: {args.esp_template}[/yellow]")

            # Create package directory
            package_dir = os.path.abspath(args.package)
            os.makedirs(package_dir, exist_ok=True)

            # Build package
            if not quiet_mode and RICH_AVAILABLE:
                with self.console.status("[bold blue]Building package..."):
                    success, package_path, package_info = builder.build_complete_package(
                        classification_results, mod_name, package_dir, options
                    )
            else:
                print("Building package...")
                success, package_path, package_info = builder.build_complete_package(
                    classification_results, mod_name, package_dir, options
                )

            if success:
                # Show success message
                if not quiet_mode and RICH_AVAILABLE:
                    self.console.print(f"\n[bold green]🎉 Package created successfully![/bold green]")
                    self.console.print(f"[green]📦 Package: {package_path}[/green]")

                    # Show package details
                    if package_info.get('components'):
                        table = Table(title="Package Contents", box=box.ROUNDED)
                        table.add_column("Component", style="cyan")
                        table.add_column("Type", style="magenta")
                        table.add_column("Size", style="green")
                        table.add_column("Files", style="yellow")

                        for comp_name, comp_info in package_info['components'].items():
                            comp_type = comp_name.replace('_', ' ').title()
                            size = f"{comp_info.get('info', {}).get('size_mb', 0):.1f} MB"
                            file_count = str(comp_info.get('file_count', 'N/A'))
                            table.add_row(comp_type, comp_type, size, file_count)

                        self.console.print(table)
                else:
                    print(f"🎉 Package created: {package_path}")

                return {
                    'success': True,
                    'package_path': package_path,
                    'package_info': package_info
                }
            else:
                if not quiet_mode:
                    self.console.print("[red]❌ Package creation failed[/red]")
                else:
                    print("❌ Package creation failed")

                return {'success': False, 'message': 'Package creation failed'}

        except Exception as e:
            error_msg = f"Packaging error: {e}"
            if not quiet_mode:
                self.console.print(f"[red]❌ {error_msg}[/red]")
            else:
                print(f"❌ {error_msg}")

            return {'success': False, 'message': error_msg}


def enhanced_main():
    """Enhanced main function with beautiful CLI."""
    cli = EnhancedCLI()

    # Check if rich is available
    if not RICH_AVAILABLE:
        print("⚠️  Enhanced CLI features require additional packages.")
        print("Install with: pip install rich click colorama")
        print("Falling back to basic CLI...\n")

        # Fall back to original CLI
        from .cli import main
        return main()

    cli.print_banner()

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="🧠 Safe Resource Packer - Enhanced CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help ourselves
    )

    parser.add_argument('--source', help='Path to source files')
    parser.add_argument('--generated', help='Path to generated files')
    parser.add_argument('--output-pack', help='Path for packable files')
    parser.add_argument('--output-loose', help='Path for loose files')
    parser.add_argument('--threads', type=int, default=8, help='Number of threads')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--log', default='safe_resource_packer.log', help='Log file path')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--validate', action='store_true', help='Validate paths only')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode (minimal output)')
    parser.add_argument('--clean', action='store_true', help='Clean output (less verbose)')
    parser.add_argument('--philosophy', action='store_true', help='Show philosophy and purpose')

    # Packaging arguments
    parser.add_argument('--package', help='Create complete mod package at this path')
    parser.add_argument('--mod-name', help='Name for the mod package')
    parser.add_argument('--game-type', choices=['skyrim', 'fallout4'], default='skyrim',
                       help='Target game (skyrim or fallout4)')
    parser.add_argument('--game-path', help='Path to game installation for bulletproof directory detection')
    parser.add_argument('--esp-template', help='Path to ESP template file')
    parser.add_argument('--compression', type=int, choices=range(0, 10), default=5,
                       help='7z compression level (0-9, higher = smaller)')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Keep temporary packaging files')
    parser.add_argument('--install-bsarch', action='store_true',
                       help='Install BSArch for optimal BSA/BA2 creation')

    parser.add_argument('--help', action='store_true', help='Show help')

    args = parser.parse_args()

    # If no arguments provided, launch console UI
    if len(sys.argv) == 1:
        from .console_ui import run_console_ui
        cli.console.print("[bold blue]🚀 Launching Interactive Console UI...[/bold blue]\n")

        config = run_console_ui()
        if not config:
            return 0  # User cancelled

        # Convert UI config to args object
        for key, value in config.items():
            if hasattr(args, key):
                setattr(args, key, value)

        # Set defaults for missing required args
        if not hasattr(args, 'log') or not args.log:
            args.log = 'safe_resource_packer.log'

    if args.help:
        cli.print_help_table()
        return 0

    if args.philosophy:
        cli.show_philosophy()
        return 0

    # Handle BSArch installation
    if args.install_bsarch:
        from .packaging.bsarch_installer import install_bsarch_if_needed
        cli.console.print("\n🔧 Installing BSArch for optimal BSA/BA2 creation...")
        success = install_bsarch_if_needed(interactive=True)
        if success:
            cli.console.print("✅ BSArch installation completed!")
        else:
            cli.console.print("❌ BSArch installation failed or was cancelled")
        return 0 if success else 1

    # Interactive mode
    if args.interactive:
        config = cli.interactive_mode()
        if not config:
            return 1

        # Update args with interactive config
        for key, value in config.items():
            setattr(args, key.replace('-', '_'), value)

    # Validate required arguments
    required_args = ['source', 'generated', 'output_pack', 'output_loose']
    missing_args = [arg for arg in required_args if not getattr(args, arg, None)]

    if missing_args and not args.validate:
        cli.console.print(f"[red]❌ Missing required arguments: {', '.join(missing_args)}[/red]")
        cli.console.print("💡 Use [cyan]--interactive[/cyan] mode or [cyan]--help[/cyan] for guidance")
        return 1

    # Validate paths
    if args.validate or not missing_args:
        cli.console.print(Panel.fit("🔍 Validating paths...", border_style="yellow"))

        validation_passed = True
        for arg_name, path_type in [
            ('source', 'source'),
            ('generated', 'generated'),
            ('output_pack', 'output pack'),
            ('output_loose', 'output loose')
        ]:
            path = getattr(args, arg_name, None)
            if path:
                valid, message = cli.validate_path(path, path_type)
                if valid:
                    cli.console.print(f"[green]✓ {message}[/green]")
                else:
                    cli.console.print(f"[red]❌ {message}[/red]")
                    validation_passed = False

        if args.validate:
            return 0 if validation_passed else 1

        if not validation_passed:
            return 1

    # Set debug mode
    set_debug(args.debug)

    # Check for quiet or clean mode
    quiet_mode = getattr(args, 'quiet', False)
    clean_mode = getattr(args, 'clean', False) or quiet_mode

    # Create packer
    game_path = getattr(args, 'game_path', None)
    game_type = getattr(args, 'game_type', 'skyrim')
    cli.packer = SafeResourcePacker(
        threads=args.threads,
        debug=args.debug,
        game_path=game_path,
        game_type=game_type
    )

    # Enhance classifier for cleaner output
    if clean_mode:
        enhance_classifier_output(cli.packer.classifier, quiet=quiet_mode)

    try:
        import time
        start_time = time.time()

        if not quiet_mode:
            cli.console.print(Panel.fit(
                f"🚀 Starting processing...\n"
                f"📁 Source: [cyan]{args.source}[/cyan]\n"
                f"🔧 Generated: [cyan]{args.generated}[/cyan]\n"
                f"📦 Pack output: [cyan]{args.output_pack}[/cyan]\n"
                f"📁 Loose output: [cyan]{args.output_loose}[/cyan]",
                title="Processing Configuration",
                border_style="blue"
            ))

        # Create clean progress callback
        if clean_mode or quiet_mode:
            progress_callback = create_clean_progress_callback(cli.console, quiet_mode)
        else:
            progress_callback = None

        # Process resources with clean output
        pack_count, loose_count, skip_count = cli.packer.process_resources(
            args.source, args.generated, args.output_pack, args.output_loose, progress_callback
        )

        processing_time = time.time() - start_time
        skipped = get_skipped()

        # Packaging phase (if requested)
        package_info = {}
        if args.package:
            package_info = cli._handle_packaging(args, pack_count, loose_count, quiet_mode)

        # Show results
        if not quiet_mode:
            cli.console.print("\n" + "="*60)
            cli.console.print("[bold green]🎉 Processing completed successfully![/bold green]")
            if package_info.get('success'):
                cli.console.print("[bold green]📦 Package created successfully![/bold green]")
            cli.console.print("="*60)
        else:
            print(f"\n✅ Completed: {pack_count} pack, {loose_count} loose, {skip_count} skip")
            if package_info.get('success'):
                print(f"📦 Package: {package_info.get('package_path', 'Created')}")

        if not quiet_mode:
            cli.print_summary_table(pack_count, loose_count, skip_count, skipped, processing_time)
            cli.print_file_tree_summary(args.output_pack, args.output_loose)
            cli.print_next_steps(pack_count, loose_count)

            # Write log
            write_log_file(args.log)
            cli.console.print(f"\n📋 Detailed log written to: [cyan]{args.log}[/cyan]")
        else:
            # Minimal output for quiet mode
            write_log_file(args.log)
            print(f"📋 Log: {args.log}")

        return 0

    except KeyboardInterrupt:
        cli.console.print("\n[yellow]⚠️  Process interrupted by user[/yellow]")
        return 1
    except Exception as e:
        cli.console.print(f"\n[red]❌ Error: {e}[/red]")
        return 1
    finally:
        if cli.packer:
            cli.packer.cleanup_temp()


def execute_with_config(config):
    """
    Execute Safe Resource Packer with configuration from console UI.

    Args:
        config: Dictionary containing configuration options

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Convert config dict to command line args format
        args = []

        # Required arguments
        if 'source' in config:
            args.extend(['--source', config['source']])
        if 'generated' in config:
            args.extend(['--generated', config['generated']])

        # Output arguments
        if 'output_pack' in config:
            args.extend(['--output-pack', config['output_pack']])
        if 'output_loose' in config:
            args.extend(['--output-loose', config['output_loose']])
        if 'package' in config:
            args.extend(['--package', config['package']])

        # Optional arguments
        if 'mod_name' in config:
            args.extend(['--mod-name', config['mod_name']])
        if 'game_type' in config:
            args.extend(['--game-type', config['game_type']])
        if 'game_path' in config and config['game_path']:
            args.extend(['--game-path', config['game_path']])
        if 'log' in config:
            args.extend(['--log', config['log']])
        if config.get('debug'):
            args.append('--debug')
        if config.get('install_bsarch'):
            args.append('--install-bsarch')
        if 'threads' in config:
            args.extend(['--threads', str(config['threads'])])

        # Parse arguments and execute
        import sys
        original_argv = sys.argv[:]
        try:
            sys.argv = ['safe-resource-packer'] + args
            return enhanced_main()
        finally:
            sys.argv = original_argv

    except Exception as e:
        print(f"❌ Error executing with config: {e}")
        return 1


if __name__ == '__main__':
    exit_code = enhanced_main()
    sys.exit(exit_code)
