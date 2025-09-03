# CLI Reference

Beginner note: If you’re non‑technical on Windows, use [[Windows_Launcher_Guide]] (double‑click launcher installs dependencies and opens the UI). The CLI below is great once you’re comfortable.

Basic usage:

```bash
safe-resource-packer --source /path/to/Data --generated /path/to/BodySlide \
                     --output-pack ./pack --output-loose ./loose
```

Core options:

-   --source PATH: Source (e.g., Skyrim/Fallout Data)
-   --generated PATH: Generated files (e.g., BodySlide output)
-   --output-pack PATH: Directory for packable files
-   --output-loose PATH: Directory for loose overrides
-   --threads N: Number of threads (default: 8)
-   --debug: Enable debug logging
-   --log FILE: Log file path (default: safe_resource_packer.log)
-   --interactive: Guided setup mode
-   --validate: Validate paths only and exit
-   --quiet: Minimal output
-   --clean: Cleaner output formatting
-   --philosophy: Show problem/solution overview

Packaging options:

-   --package PATH: Create complete package in PATH
-   --mod-name NAME: Package name (default: from generated path)
-   --game-type {skyrim,fallout4}: Target game (default: skyrim)
-   --esp-template FILE: Custom ESP template
-   --compression 0-9: 7z compression (default: 5)
-   --no-cleanup: Keep temporary packaging files
-   --install-bsarch: Install BSArch for optimal BSA/BA2 creation

Help:

```bash
safe-resource-packer --help
```
