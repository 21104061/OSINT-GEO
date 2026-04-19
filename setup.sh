#!/bin/bash

# OBSIDIAN OSINT - Automated Setup Script for macOS/Linux
# This script automatically installs and configures the entire system
# Security Updates: Flask 3.1.3, Flask-CORS 6.0.2, Requests 2.33.0

echo ""
echo "============================================"
echo "  OBSIDIAN OSINT - Setup Wizard"
echo "  Automated Installation for macOS/Linux"
echo "  [Security Updates Applied]"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    echo ""
    exit 1
fi

python3 --version
echo ""

# Step 1: Create virtual environment
echo "[1/4] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
fi
echo ""

# Step 2: Activate virtual environment and install dependencies
echo "[2/4] Installing dependencies..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

# Step 3: Create data directory if it doesn't exist
echo "[3/4] Setting up data storage..."
mkdir -p data
echo "Data directory ready!"
echo ""

# Step 4: Display instructions and launch
echo "[4/4] Launching application..."
echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "The backend server is starting now."
echo "Once it's running, open another terminal and run:"
echo ""
echo "  cd $(pwd)"
echo "  source .venv/bin/activate"
echo "  python -m http.server 8000"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:8000/index.html"
echo ""
echo "Press Enter to start the backend..."
echo ""
read

# Launch backend
echo "Starting backend server on http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

python backend.py
