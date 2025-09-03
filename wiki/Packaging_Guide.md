# Packaging Guide

Create a professional mod package with one command:

```bash
safe-resource-packer --source ./Data --generated ./BodySlide_Output \
                     --output-pack ./pack --output-loose ./loose \
                     --package ./MyMod_Package --mod-name "SexyArmorMod" \
                     --game-type skyrim --compression 5
```

What it produces:

-   ESP that loads the archive
-   BSA/BA2 archive of packable files
-   7z of loose overrides
-   Final `SexyArmorMod_v1.0.7z` containing all components and metadata

ESP templates:

-   Included templates: `src/safe_resource_packer/templates/esp/`
-   Provide your own via `--esp-template FILE`

BSArch (recommended):

```bash
safe-resource-packer --install-bsarch
```

-   If unavailable, ZIP fallback is used for archives

Tips:

-   Use a clean `generated` folder containing only BodySlide output
-   Keep overrides as loose files for compatibility
