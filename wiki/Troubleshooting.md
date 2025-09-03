# Troubleshooting

Tip for non‑technical Windows users: Start with [[Windows_Launcher_Guide]]. The launcher auto‑installs dependencies and opens the UI.

Missing required arguments:

-   Use `--interactive` or see [[CLI_Reference]]

Invalid paths:

-   Ensure `--source` and `--generated` exist and are directories
-   Use absolute paths for reliability

BSArch not found:

-   Run `safe-resource-packer --install-bsarch`
-   See `BSARCH_INSTALLATION_GUIDE.md`

Slow output or noisy logs:

-   Use `--threads 16` on modern CPUs
-   Add `--clean` or `--quiet`

Rich not installed:

-   `pip install rich click colorama`

Crashes or errors:

-   Re-run with `--debug` and check the log file
