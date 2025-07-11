#!/usr/bin/env python3
"""
Install required dependencies for video generation
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install all required packages"""
    print("📦 Installing video generation dependencies...\n")
    
    # Required packages for video generation
    packages = [
        "replicate",           # For Replicate API
        "moviepy",            # For video processing
        "Pillow>=8.0.0",      # For image processing
        "requests>=2.25.0",   # For API calls
        "python-decouple",    # For environment variables
        "celery[redis]",      # For background tasks (optional)
        "redis",              # For Celery broker (optional)
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
        print()
    
    if failed_packages:
        print(f"⚠️  Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return False
    else:
        print("✅ All dependencies installed successfully!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
