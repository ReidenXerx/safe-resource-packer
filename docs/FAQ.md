# FAQ

Beginner note: On Windows, the fastest path is [[Windows_Launcher_Guide]] (double‑click launcher installs everything and opens the UI).

Q: What are Pack, Loose, and Skip?
A: Pack = new content safe for archives; Loose = overrides that must stay loose; Skip = identical files.

Q: Does SRP modify my originals?
A: No. It reads sources and writes outputs to your chosen directories.

Q: Do I need BSArch?
A: Recommended. `--install-bsarch` helps set it up. ZIP fallback still works.

Q: Supported games?
A: `--game-type` supports `skyrim` and `fallout4`.

Q: Minimum Python?
A: Python >= 3.7.

Q: Where is the log?
A: `safe_resource_packer.log` by default, configurable with `--log`.

Q: How many threads by default?
A: 8.

Q: How do I launch the UI?
A: `safe-resource-packer` (main command) or `safe-resource-packer-ui` (console UI).

Q: What do the debug messages mean?
A: See [[Debug_Status_Guide]] for complete explanation of all status messages.

Q: When should I use debug mode?
A: For troubleshooting. Regular use: clean mode is much more pleasant.

Q: What do the colored debug messages mean?
A: Green = found match, Blue = new file, Yellow = skip, Magenta = override, Red = error.
