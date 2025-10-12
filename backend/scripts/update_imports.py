"""
Helper script to update import statements after project restructuring

Usage:
    python scripts/update_imports.py [--dry-run] [--path PATH]
    
    --dry-run: Show what would be changed without making changes
    --path: Specific file or directory to update (default: entire project)
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Define import replacements
IMPORT_REPLACEMENTS = [
    # Model imports
    (r'from models\.', 'from src.models.architectures.'),
    (r'import models\.', 'import src.models.architectures.'),
    
    # Utils imports
    (r'from utils\.', 'from src.data.utils.'),
    (r'import utils\.', 'import src.data.utils.'),
    
    # Preprocessing imports
    (r'from preprocessing\.', 'from src.data.preprocessing.'),
    (r'import preprocessing\.', 'import src.data.preprocessing.'),
]

# Define path replacements
PATH_REPLACEMENTS = [
    # Dataset paths
    (r'"datasets/', '"data/raw/datasets/'),
    (r"'datasets/", "'data/raw/datasets/"),
    
    # Checkpoint paths
    (r'"checkpoints/', '"saved_models/checkpoints/pretrained/'),
    (r"'checkpoints/", "'saved_models/checkpoints/pretrained/"),
    
    # Output paths
    (r'"outputs/', '"saved_models/final/'),
    (r"'outputs/", "'saved_models/final/"),
]

def update_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Update imports and paths in a single file
    
    Returns:
        (changed, num_changes): Whether file was changed and number of changes
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False, 0
    
    original_content = content
    num_changes = 0
    
    # Update imports
    for pattern, replacement in IMPORT_REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            matches = len(re.findall(pattern, content))
            num_changes += matches
            content = new_content
    
    # Update paths
    for pattern, replacement in PATH_REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            matches = len(re.findall(pattern, content))
            num_changes += matches
            content = new_content
    
    if content != original_content:
        if not dry_run:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {filepath} ({num_changes} changes)")
            except Exception as e:
                print(f"❌ Error writing {filepath}: {e}")
                return False, 0
        else:
            print(f"🔍 Would update {filepath} ({num_changes} changes)")
        return True, num_changes
    
    return False, 0

def find_python_files(root_path: Path, exclude_dirs: List[str] = None) -> List[Path]:
    """Find all Python files in directory"""
    if exclude_dirs is None:
        exclude_dirs = [
            '__pycache__', '.git', 'venv', 'env', 'crowdenv',
            'node_modules', '.pytest_cache', '.tox', 'build',
            'dist', 'egg-info', '.ipynb_checkpoints'
        ]
    
    python_files = []
    
    if root_path.is_file():
        if root_path.suffix == '.py':
            python_files.append(root_path)
    else:
        for py_file in root_path.rglob('*.py'):
            # Check if file is in excluded directory
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            python_files.append(py_file)
    
    return python_files

def main():
    parser = argparse.ArgumentParser(
        description='Update import statements after project restructuring'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Specific file or directory to update (default: current directory)'
    )
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    
    if not root_path.exists():
        print(f"❌ Path does not exist: {root_path}")
        return
    
    print(f"🔍 Scanning for Python files in: {root_path}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    print()
    
    # Find all Python files
    python_files = find_python_files(root_path)
    
    if not python_files:
        print("❌ No Python files found")
        return
    
    print(f"📁 Found {len(python_files)} Python files")
    print()
    
    # Update each file
    total_files_changed = 0
    total_changes = 0
    
    for filepath in python_files:
        changed, num_changes = update_file(filepath, args.dry_run)
        if changed:
            total_files_changed += 1
            total_changes += num_changes
    
    print()
    print("=" * 60)
    print(f"✨ Summary:")
    print(f"   Files scanned: {len(python_files)}")
    print(f"   Files changed: {total_files_changed}")
    print(f"   Total changes: {total_changes}")
    
    if args.dry_run:
        print()
        print("🔍 This was a dry run. Run without --dry-run to apply changes.")
    else:
        print()
        print("✅ Import updates complete!")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
