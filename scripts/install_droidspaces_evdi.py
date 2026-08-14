#!/usr/bin/env python3
"""Install the extend-only EVDI source into an official common kernel tree.

The driver source is maintained independently from the common kernel.  This
installer performs only the two required DRM registration edits and refuses
ambiguous or partially modified trees.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


SOURCE_FILES = (
    "Kconfig",
    "LICENSE",
    "Makefile",
    "evdi_connector.c",
    "evdi_drv.h",
    "evdi_event.c",
    "evdi_fb.c",
    "evdi_gem.c",
    "evdi_ioctl.c",
    "evdi_lindroid_drv.c",
    "evdi_modeset.c",
    "evdi_sysfs.c",
    "uapi/evdi_drm.h",
)

KCONFIG_ANCHOR = 'source "drivers/gpu/drm/nouveau/Kconfig"'
KCONFIG_LINE = 'source "drivers/gpu/drm/evdi/Kconfig"'
MAKEFILE_ANCHOR = "obj-$(CONFIG_DRM_TTM)"
MAKEFILE_LINE = "obj-$(CONFIG_DRM_LINDROID_EVDI) += evdi/"


class InstallError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--common", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    return parser.parse_args()


def read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError as error:
        raise InstallError(f"cannot read {path}: {error}") from error


def insert_once(content: str, anchor: str, line: str, path: Path) -> str:
    lines = content.splitlines(keepends=True)
    normalized = [item.rstrip("\r\n") for item in lines]
    # Kernel Makefiles align assignments with tabs, so the stable anchor is
    # the CONFIG symbol rather than its surrounding whitespace.
    anchor_indexes = [i for i, item in enumerate(normalized) if item == anchor or item.startswith(anchor + "\t")]
    line_indexes = [i for i, item in enumerate(normalized) if item == line]
    if len(anchor_indexes) != 1:
        raise InstallError(f"expected one anchor {anchor!r} in {path}, found {len(anchor_indexes)}")
    if len(line_indexes) > 1:
        raise InstallError(f"duplicate EVDI integration line in {path}")
    if line_indexes:
        return content
    index = anchor_indexes[0]
    newline = "\r\n" if "\r\n" in content else "\n"
    lines.insert(index, line + newline)
    return "".join(lines)


def install_source(source_dir: Path, destination: Path) -> None:
    missing = [name for name in SOURCE_FILES if not (source_dir / name).is_file()]
    if missing:
        raise InstallError(f"EVDI source is incomplete: {', '.join(missing)}")

    destination.mkdir(parents=True, exist_ok=True)
    for name in SOURCE_FILES:
        source = source_dir / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if not filecmp.cmp(source, target, shallow=False):
                raise InstallError(f"existing EVDI file differs: {target}")
        else:
            shutil.copy2(source, target)


def main() -> None:
    args = parse_args()
    common = args.common.resolve()
    source_dir = args.source_dir.resolve()
    drm_dir = common / "drivers/gpu/drm"
    kconfig = drm_dir / "Kconfig"
    makefile = drm_dir / "Makefile"
    destination = drm_dir / "evdi"

    if not kconfig.is_file() or not makefile.is_file():
        raise SystemExit(f"official common DRM files not found below {common}")

    try:
        install_source(source_dir, destination)
        kconfig_content = insert_once(read(kconfig), KCONFIG_ANCHOR, KCONFIG_LINE, kconfig)
        makefile_content = insert_once(read(makefile), MAKEFILE_ANCHOR, MAKEFILE_LINE, makefile)
        kconfig.write_text(kconfig_content)
        makefile.write_text(makefile_content)
    except InstallError as error:
        raise SystemExit(f"DroidSpaces EVDI installation failed: {error}") from error

    print(f"Installed extend-only EVDI into {destination}")
    print("Registered EVDI in drivers/gpu/drm/{Kconfig,Makefile}")


if __name__ == "__main__":
    main()
