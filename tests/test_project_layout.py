"""Checks that the project directory layout matches what the code expects."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from SAXS_asymmetry import paths


class ProjectLayoutTests(unittest.TestCase):
    def test_project_root_contains_pyproject(self) -> None:
        self.assertTrue((paths.PROJECT_ROOT / "pyproject.toml").is_file())

    def test_package_lives_under_src(self) -> None:
        self.assertEqual(paths.SRC_DIR.name, "src")
        self.assertEqual(paths.PACKAGE_DIR.name, "SAXS_asymmetry")

    def test_data_tree_is_outside_the_package(self) -> None:
        self.assertEqual(paths.DATA_DIR, paths.PROJECT_ROOT / "data")
        for directory in (paths.EXPERIMENTAL_DIR, paths.PROFILES_DIR, paths.REFERENCE_DIR):
            self.assertTrue(directory.is_dir(), directory)

    def test_outputs_tree_is_outside_the_package(self) -> None:
        self.assertEqual(
            paths.OUTPUTS_DIR, paths.PROJECT_ROOT / "outputs" / "saxs_asymmetry"
        )

    def test_notebooks_tree_is_outside_the_package(self) -> None:
        self.assertTrue(
            (paths.NOTEBOOKS_DIR / "01_calculate_and_save_data.ipynb").is_file()
        )

    def test_no_data_or_outputs_remain_in_the_package(self) -> None:
        for leftover in ("inputs", "outputs"):
            self.assertFalse((paths.PACKAGE_DIR / leftover).exists(), leftover)
        self.assertEqual(list(paths.PACKAGE_DIR.glob("*.ipynb")), [])


class EnvironmentOverrideTests(unittest.TestCase):
    def test_output_dir_honours_env_override(self) -> None:
        import importlib

        previous = os.environ.get("PCI_OUTPUT_DIR")
        override = Path(__file__).resolve().parent
        os.environ["PCI_OUTPUT_DIR"] = str(override)
        try:
            reloaded = importlib.reload(paths)
            self.assertEqual(reloaded.OUTPUTS_DIR, override)
        finally:
            if previous is None:
                del os.environ["PCI_OUTPUT_DIR"]
            else:
                os.environ["PCI_OUTPUT_DIR"] = previous
            importlib.reload(paths)


if __name__ == "__main__":
    unittest.main()
