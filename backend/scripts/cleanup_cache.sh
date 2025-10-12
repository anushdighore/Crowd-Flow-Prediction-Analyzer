#!/bin/bash
# Cleanup Script for Backend (Linux/Mac)
# Removes scattered cache files and consolidates them in target/

echo "🧹 Cleaning up backend cache files..."

# Remove existing __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove existing .pytest_cache
echo "Removing .pytest_cache..."
rm -rf .pytest_cache

# Remove Python compiled files
echo "Removing .pyc files..."
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Create target directory if not exists
mkdir -p target/pycache
mkdir -p target/.pytest_cache

echo "✅ Cleanup complete!"
echo ""
echo "📦 Cache will now be stored in:"
echo "   - target/pycache/          (Python bytecode)"
echo "   - target/.pytest_cache/    (Pytest cache)"
echo ""
echo "💡 To apply settings, run:"
echo "   export PYTHONPYCACHEPREFIX=target/pycache"
echo "   OR add to .env and use python-dotenv"
