"""Build a distributable archive bundling the Flask backend and frontend build."""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
PACKAGE_DIR = BUILD_DIR / "gestao-parceiros"
ZIP_PATH = BUILD_DIR / "gestao-parceiros.zip"

IGNORED_PATTERNS = ("__pycache__", "*.pyc", "*.pyo")

ITEMS_TO_INCLUDE = (
    ("app.py", "app.py"),
    ("desktop.py", "desktop.py"),
    ("export_utils.py", "export_utils.py"),
    ("models.py", "models.py"),
    ("requirements.txt", "requirements.txt"),
    ("config", "config"),
    ("templates", "templates"),
    ("static", "static"),
    (FRONTEND_DIST, Path("frontend") / "dist"),
)


def ensure_frontend_build() -> None:
    """Validate that the frontend build artefacts are available."""

    if not FRONTEND_DIST.exists():
        sys.exit(
            "Frontend build not found. Run 'npm run build' inside the 'frontend/' folder before packaging."
        )


def reset_build_directory() -> None:
    """Clean previous build outputs and recreate the directory structure."""

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)


def copy_item(source: Path | str, destination: Path | str) -> None:
    """Copy a file or directory into the package directory."""

    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source_path

    destination_path = PACKAGE_DIR / Path(destination)

    if not source_path.exists():
        raise FileNotFoundError(f"Cannot package missing path: {source_path}")

    if source_path.is_dir():
        shutil.copytree(
            source_path,
            destination_path,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(*IGNORED_PATTERNS),
        )
    else:
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def populate_package() -> None:
    """Copy all required files into the staging directory."""

    for source, destination in ITEMS_TO_INCLUDE:
        copy_item(source, destination)


def create_archive() -> None:
    """Compress the staged files into a zip archive."""

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in PACKAGE_DIR.rglob("*"):
            archive_path = file_path.relative_to(BUILD_DIR)
            archive.write(file_path, arcname=archive_path)



def main() -> None:
    ensure_frontend_build()
    reset_build_directory()
    populate_package()
    create_archive()
    print(f"Created package at {ZIP_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
