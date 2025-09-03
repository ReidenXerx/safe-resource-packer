# Getting Started

This guide helps you run Safe Resource Packer in minutes.

Beginner (Windows) – Recommended:

-   Double‑click `Safe_Resource_Packer.bat` (from release zip)
-   The launcher installs Python and dependencies automatically
-   It opens the Console UI that guides you step‑by‑step

If PowerShell blocks `.ps1`, use the `.bat` launcher or see [[Windows_Launcher_Guide]].

Prerequisites:

-   Python 3.7+ (Windows users can use the portable launcher)
-   Optional: rich, click, colorama for enhanced CLI

Quick install (dev mode):

```bash
git clone https://github.com/ReidenXerx/safe-resource-packer.git
cd safe-resource-packer
pip install -e .
```

One-command complete packaging:

```bash
safe-resource-packer --source ./Data --generated ./BodySlide_Output \
                     --package ./MyMod --mod-name "MyMod" \
                     --game-type skyrim
```

Interactive console UI:

```bash
safe-resource-packer
# or
safe-resource-packer-ui
```

Next steps:

-   See [[Windows_Launcher_Guide]] if you’re non‑technical (start here)
-   See [[Console_UI_Guide]] for the interactive flow
-   See [[CLI_Reference]] for all options
-   See [[Packaging_Guide]] to create BSA/BA2 + ESP + Loose 7z
