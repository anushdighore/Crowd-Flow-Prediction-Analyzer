"""Utility to consolidate Python bytecode cache files into a single folder.

Usage (from repository root):
    python scripts/collect_pycache.py --root ml

By default the script copies every ``*.pyc`` file found under ``--root`` into
``<root>/_collected_pycache`` while preserving the original directory structure.

Pass ``--flatten`` to place all files in a single flat folder with hashed file
names, or ``--move`` to move the cache files instead of copying.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from typing import Iterable, Set


def find_pyc_files(root: Path) -> Iterable[Path]:
    """Yield all ``*.pyc`` files beneath *root*."""
    yield from root.rglob("*.pyc")


def resolve_output_path(root: Path, output: Path) -> Path:
    """Resolve *output* relative to *root* when needed."""
    return output if output.is_absolute() else root / output


def sanitize_name(rel_path: Path) -> str:
    """Create a flattened filename that encodes the original relative path."""
    digest = hashlib.sha1(str(rel_path).encode("utf-8")).hexdigest()[:8]
    return f"{rel_path.stem}-{digest}{rel_path.suffix}"


def copy_or_move(src: Path, dest: Path, move: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(src), str(dest))
    else:
        shutil.copy2(src, dest)


def collect_pycache(root: Path, output: Path, *, flatten: bool, move: bool) -> tuple[int, int]:
    """
    Collect ``*.pyc`` files from *root* into *output*.

    Returns a tuple of (files_processed, unique_directories_touched).
    """
    files_processed = 0
    directories: Set[Path] = set()

    for pyc_file in find_pyc_files(root):
        rel_path = pyc_file.relative_to(root)
        directories.add(pyc_file.parent)

        if flatten:
            dest = output / sanitize_name(rel_path)
        else:
            dest = output / rel_path

        copy_or_move(pyc_file, dest, move)
        files_processed += 1

    return files_processed, len(directories)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Python cache files into one folder")
    parser.add_argument("--root", default="ml", type=Path, help="Directory to scan for __pycache__ folders")
    parser.add_argument(
        "--output",
        default="_collected_pycache",
        type=Path,
        help="Destination folder (relative to --root unless absolute)",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="Store files in a flat directory using hashed filenames",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying them",
    )
    parser.add_argument(
        "--remove-empty",
        action="store_true",
        help="Remove empty __pycache__ directories after processing",
    )
    return parser.parse_args()


def remove_empty_pycache_dirs(root: Path) -> int:
    removed = 0
    for cache_dir in root.rglob("__pycache__"):
        try:
            if not any(cache_dir.iterdir()):
                cache_dir.rmdir()
                removed += 1
        except FileNotFoundError:
            continue
    return removed


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output = resolve_output_path(root, args.output)

    if not root.exists():
        raise SystemExit(f"Root directory does not exist: {root}")

    output.mkdir(parents=True, exist_ok=True)

    files_processed, directory_count = collect_pycache(
        root, output, flatten=args.flatten, move=args.move
    )

    removed = remove_empty_pycache_dirs(root) if args.remove_empty else 0

    print("=== PyCache Collection Summary ===")
    print(f"Root scanned: {root}")
    print(f"Output folder: {output}")
    print(f"Files processed: {files_processed}")
    print(f"__pycache__ directories touched: {directory_count}")
    if args.move:
        print("Action: moved files into the output folder")
    else:
        print("Action: copied files into the output folder")
    if args.flatten:
        print("Layout: flattened (hashed filenames)")
    else:
        print("Layout: preserved original directory structure")
    if args.remove_empty:
        print(f"Empty __pycache__ folders removed: {removed}")


if __name__ == "__main__":
    main()
