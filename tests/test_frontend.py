from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def test_frontend_unit_tests():
    """Run the Vitest suite so the pipeline validates the frontend."""

    npm_path = shutil.which("npm")
    if npm_path is None:
        pytest.skip("npm is required to run the frontend test suite")

    project_root = Path(__file__).resolve().parents[1]
    frontend_dir = project_root / "frontend"

    dependencies_installed = (frontend_dir / "node_modules").exists() and (
        (frontend_dir / "node_modules" / ".bin" / "vitest").exists()
    )

    if not dependencies_installed:
        pytest.skip("Frontend dependencies are not installed")

    result = subprocess.run(
        [npm_path, "run", "test", "--", "--run"],
        cwd=frontend_dir,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.fail(
            "Frontend tests failed\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
