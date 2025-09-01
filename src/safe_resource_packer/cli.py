"""
Command-line interface for Safe Resource Packer.
"""

import argparse
import sys
from .core import SafeResourcePacker
from .utils import log, write_log_file, set_debug, get_skipped


def main():
    """Main CLI entry point - tries enhanced CLI first, falls back to basic."""
    try:
        from .enhanced_cli import enhanced_main
        return enhanced_main()
    except ImportError:
        # Fall back to basic CLI if enhanced dependencies aren't available
        return basic_main()


def basic_main():
    """Basic CLI entry point without enhanced features."""
    parser = argparse.ArgumentParser(
        description="🧠 Safe Resource Packer for Skyrim (Path Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source /path/to/data --generated /path/to/bodyslide --output-pack ./pack --output-loose ./loose
  %(prog)s --source ./data --generated ./generated --output-pack ./pack --output-loose ./loose --threads 16 --debug
        """
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Path to final Data folder or Vortex deployed repo'
    )
    parser.add_argument(
        '--generated',
        required=True,
        help='Path to generated resources folder (e.g. BodySlide output)'
    )
    parser.add_argument(
        '--output-pack',
        required=True,
        help='Path to copy safe-to-pack files'
    )
    parser.add_argument(
        '--output-loose',
        required=True,
        help='Path to copy override files (should stay loose)'
    )
    parser.add_argument(
        '--log',
        default='safe_resource_packer.log',
        help='Path to log output file (default: safe_resource_packer.log)'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=8,
        help='Number of threads to use (default: 8)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Set debug mode
    set_debug(args.debug)

    # Create packer instance
    packer = SafeResourcePacker(threads=args.threads, debug=args.debug)

    try:
        log("Starting Safe Resource Packer...")
        log(f"Source: {args.source}")
        log(f"Generated: {args.generated}")
        log(f"Output Pack: {args.output_pack}")
        log(f"Output Loose: {args.output_loose}")
        log(f"Threads: {args.threads}")
        log(f"Debug: {args.debug}")

        # Process resources
        pack_count, loose_count, skip_count = packer.process_resources(
            args.source,
            args.generated,
            args.output_pack,
            args.output_loose
        )

        # Print summary
        log("\n===== SUMMARY =====")
        log(f"Classified for packing (new): {pack_count}")
        log(f"Classified for loose (override): {loose_count}")
        log(f"Skipped (identical): {skip_count}")

        skipped = get_skipped()
        log(f"Skipped or errored: {len(skipped)}")

        if skipped:
            log("\n⚠️  Some files were skipped due to errors:")
            for s in skipped:
                log(s)

        log("\n✅ Processing completed successfully!")

    except KeyboardInterrupt:
        log("Process interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        write_log_file(args.log)


if __name__ == '__main__':
    main()
