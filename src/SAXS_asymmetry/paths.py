"""Canonical project directory layout for the SAXS/PCI workflows.

The package lives in ``src/SAXS_asymmetry`` while inputs, generated artifacts
and notebooks live at the project root. Importing this module keeps every entry
point (CLI scripts, Blender scripts and notebooks) pointing at the same places.

Both data directories can be redirected with environment variables, which is
useful when the repository is read-only or the artifacts live on a scratch disk:

* ``PCI_DATA_DIR`` overrides ``DATA_DIR``
* ``PCI_OUTPUT_DIR`` overrides ``OUTPUTS_DIR``
"""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent


def _resolve(env_var: str, default: Path) -> Path:
    override = os.environ.get(env_var)
    if override:
        return Path(override).expanduser().resolve()
    return default


DATA_DIR = _resolve("PCI_DATA_DIR", PROJECT_ROOT / "data")
OUTPUTS_DIR = _resolve("PCI_OUTPUT_DIR", PROJECT_ROOT / "outputs" / "saxs_asymmetry")
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks" / "saxs_asymmetry"

EXPERIMENTAL_DIR = DATA_DIR / "experimental"
PROFILES_DIR = DATA_DIR / "profiles"
REFERENCE_DIR = DATA_DIR / "reference"

__all__ = [
    "PACKAGE_DIR",
    "SRC_DIR",
    "PROJECT_ROOT",
    "DATA_DIR",
    "OUTPUTS_DIR",
    "NOTEBOOKS_DIR",
    "EXPERIMENTAL_DIR",
    "PROFILES_DIR",
    "REFERENCE_DIR",
]
