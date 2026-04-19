#!/usr/bin/env python3
"""
OBSIDIAN OSINT - Cross-Platform Setup Script
Automatically installs and runs the application on Windows, macOS, and Linux
Security Updates: Flask 3.1.4, Flask-CORS 5.1.0, Requests 2.33.0
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50 + "\n")

def check_python_version():
    """Check if Python version is 3.9+"""
    print("[1/5] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"ERROR: Python 3.9+ required, but found {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} found\n")

def create_venv():
    """Create virtual environment"""
    print("[2/5] Setting up virtual environment...")
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists\n")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✓ Virtual environment created successfully\n")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        sys.exit(1)

def install_dependencies():
    """Install required packages"""
    print("[3/5] Installing dependencies...")
    
    # Get the appropriate pip command based on OS
    if platform.system() == "Windows":
        pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
        req_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    else:
        pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
        req_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    
    try:
        subprocess.run(pip_cmd, check=True, capture_output=True)
        subprocess.run(req_cmd, check=True)
        print("✓ Dependencies installed successfully\n")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        sys.exit(1)

def setup_data_directory():
    """Create data directory"""
    print("[4/5] Setting up data storage...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✓ Data directory ready\n")

def launch_application():
    """Launch the backend and optionally frontend"""
    print("[5/5] Launching OBSIDIAN OSINT...\n")
    
    print_header("OBSIDIAN OSINT - Ready to Run")
    print("✓ Installation complete!")
    print("\nNext steps:")
    print("1. Backend will start now (you'll see the Flask server)")
    print("2. Open your browser to: http://localhost:8000/index.html")
    print("\nNote: If you want to run the frontend on a different terminal,")
    print("run this command in a new terminal window:\n")
    
    if platform.system() == "Windows":
        print("  .venv\\Scripts\\activate")
        print("  python -m http.server 8000\n")
    else:
        print("  source .venv/bin/activate")
        print("  python -m http.server 8000\n")
    
    print("Press Enter to start the backend...\n")
    input()
    
    # Get the appropriate Python executable
    if platform.system() == "Windows":
        python_exe = ".venv\\Scripts\\python.exe"
    else:
        python_exe = ".venv/bin/python"
    
    try:
        print("Starting backend server on http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server\n")
        subprocess.run([python_exe, "backend.py"], check=False)
    except KeyboardInterrupt:
        print("\n\nBackend stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Failed to start backend: {e}")
        sys.exit(1)

def main():
    """Main setup routine"""
    print_header("OBSIDIAN OSINT Setup Wizard")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python Executable: {sys.executable}\n")
    
    # Run setup steps
    check_python_version()
    create_venv()
    install_dependencies()
    setup_data_directory()
    launch_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
