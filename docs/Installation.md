# Installation

Beginner (Windows) – one‑click launcher (Recommended)

1. Download latest release ZIP
2. Extract the ZIP
3. Double‑click `run_safe_resource_packer.bat`
4. The launcher installs Python and dependencies automatically
5. The Console UI opens and guides you through setup

Option 2: Developer setup

```bash
git clone https://github.com/ReidenXerx/safe-resource-packer.git
cd safe-resource-packer
pip install -e .
```

Option 3: Python package (when available)

```bash
pip install safe-resource-packer
```

Option 4: Bundled Release (Recommended for End Users)

-   Download bundled release ZIP (includes Python)
-   Extract anywhere, run `run_safe_resource_packer.bat`
-   Zero dependencies, completely self-contained

Enhanced CLI (optional):

```bash
pip install rich click colorama
```

Troubleshooting (Windows launchers):

-   If PowerShell blocks scripts, use the `.bat` launcher or see [[Windows_Launcher_Guide]]
-   Ensure you have enough free disk space (classification + packaging uses temp space)
