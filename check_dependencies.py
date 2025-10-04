"""
Dependency Checker for Webcam Crowd Counter
Verifies all required dependencies are installed
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} - NOT INSTALLED")
        return False

def check_python_packages():
    """Check all required Python packages"""
    print("\n📦 Checking Python packages...")
    
    packages = [
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("python-multipart", "multipart"),
        ("opencv-python", "cv2"),
        ("pillow", "PIL"),
        ("numpy", "numpy"),
        ("websockets", "websockets"),
    ]
    
    all_installed = True
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
            missing_packages.append(package_name)
    
    return all_installed, missing_packages

def check_node():
    """Check if Node.js is installed"""
    print("\n🟢 Checking Node.js...")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ Node.js {version}")
            return True
        else:
            print("   ❌ Node.js - NOT FOUND")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Node.js - NOT INSTALLED")
        return False

def check_npm():
    """Check if npm is installed"""
    print("\n📦 Checking npm...")
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ npm {version}")
            return True
        else:
            print("   ❌ npm - NOT FOUND")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ npm - NOT INSTALLED")
        return False

def check_cuda():
    """Check if CUDA is available"""
    print("\n🎮 Checking CUDA (GPU support)...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   ✅ CUDA available")
            print(f"   ℹ️  Device: {torch.cuda.get_device_name(0)}")
            print(f"   ℹ️  CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("   ⚠️  CUDA not available (CPU mode will be used)")
            return False
    except ImportError:
        print("   ⚠️  Cannot check CUDA (PyTorch not installed)")
        return False

def check_checkpoint():
    """Check if model checkpoint exists"""
    print("\n🧠 Checking model checkpoint...")
    import os
    checkpoint_path = "./checkpoints/jhu_5.pth"
    
    if os.path.exists(checkpoint_path):
        size_mb = os.path.getsize(checkpoint_path) / (1024 * 1024)
        print(f"   ✅ Checkpoint found: {checkpoint_path}")
        print(f"   ℹ️  Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"   ❌ Checkpoint NOT FOUND: {checkpoint_path}")
        print("   ℹ️  Please place the model checkpoint in the checkpoints folder")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    print("\n📦 Checking frontend dependencies...")
    import os
    
    node_modules = "./crowd-counter-frontend/node_modules"
    if os.path.exists(node_modules):
        print(f"   ✅ node_modules folder exists")
        return True
    else:
        print(f"   ❌ node_modules NOT FOUND")
        print("   ℹ️  Run: cd crowd-counter-frontend && npm install")
        return False

def generate_install_commands(missing_packages):
    """Generate installation commands for missing packages"""
    if not missing_packages:
        return
    
    print("\n💡 Installation Commands:")
    print("=" * 60)
    print("\nTo install missing Python packages, run:")
    print("-" * 60)
    
    # Single command for all packages
    packages_str = " ".join(missing_packages)
    print(f"pip install {packages_str}")
    
    print("\nOr install them one by one:")
    print("-" * 60)
    for package in missing_packages:
        print(f"pip install {package}")

def main():
    """Main check function"""
    print("=" * 60)
    print("  WEBCAM CROWD COUNTER - DEPENDENCY CHECKER")
    print("=" * 60)
    
    all_ok = True
    
    # Check Python version
    if not check_python_version():
        all_ok = False
    
    # Check Python packages
    packages_ok, missing_packages = check_python_packages()
    if not packages_ok:
        all_ok = False
    
    # Check Node.js
    if not check_node():
        all_ok = False
    
    # Check npm
    if not check_npm():
        all_ok = False
    
    # Check CUDA (optional)
    check_cuda()
    
    # Check model checkpoint
    if not check_checkpoint():
        all_ok = False
    
    # Check frontend dependencies
    if not check_frontend_dependencies():
        all_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("  ✅ ALL DEPENDENCIES INSTALLED!")
        print("=" * 60)
        print("\n🎉 Your system is ready!")
        print("\nNext steps:")
        print("1. Run: start_webcam_app.bat")
        print("2. Or run: python test_webcam.py (to test)")
        print("3. Open browser: http://localhost:3000")
    else:
        print("  ❌ SOME DEPENDENCIES ARE MISSING")
        print("=" * 60)
        
        if missing_packages:
            generate_install_commands(missing_packages)
        
        print("\n📝 Additional setup needed:")
        print("-" * 60)
        
        if not check_node():
            print("• Install Node.js from: https://nodejs.org/")
        
        if not check_frontend_dependencies():
            print("• Install frontend dependencies:")
            print("  cd crowd-counter-frontend")
            print("  npm install")
        
        if not check_checkpoint():
            print("• Place model checkpoint at: ./checkpoints/jhu_5.pth")
        
        print("\nAfter installing missing dependencies, run this script again.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during check: {e}")
        import traceback
        traceback.print_exc()
