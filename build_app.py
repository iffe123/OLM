#!/usr/bin/env python3
"""
Build script to create standalone OLM Converter executable
"""

import subprocess
import sys
import os
import platform
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def install_requirements():
    """Install app requirements"""
    print("Installing app requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")
    print("This may take a few minutes...\n")

    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--name", "OLM-Converter",
        "--add-data", f"static{os.pathsep}static",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "email.parser",
        "--hidden-import", "email.policy",
        "--hidden-import", "chardet",
        "desktop_app.py"
    ])

def main():
    print("=" * 50)
    print("  OLM Converter - Build Script")
    print("=" * 50)
    print()
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print()

    # Install requirements first
    install_requirements()

    # Check/install PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()

    # Build
    build_executable()

    # Show result
    print()
    print("=" * 50)
    print("  BUILD COMPLETE!")
    print("=" * 50)
    print()

    dist_dir = os.path.join(os.path.dirname(__file__), "dist")
    if platform.system() == "Windows":
        exe_name = "OLM-Converter.exe"
    else:
        exe_name = "OLM-Converter"

    exe_path = os.path.join(dist_dir, exe_name)

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"Executable created: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print()
        print("You can now:")
        print(f"  1. Copy '{exe_name}' anywhere on your computer")
        print("  2. Double-click to run it")
        print("  3. Your browser will open automatically")
    else:
        print("Error: Executable was not created. Check the output above for errors.")

if __name__ == "__main__":
    main()
