@echo off
REM OBSIDIAN OSINT - Automated Setup Script for Windows
REM This script automatically installs and configures the entire system

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   OBSIDIAN OSINT - Setup Wizard
echo   Automated Installation for Windows
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo.

REM Step 1: Create virtual environment
echo [1/4] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

REM Step 2: Activate virtual environment and install dependencies
echo [2/4] Installing dependencies...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Step 3: Create data directory if it doesn't exist
echo [3/4] Setting up data storage...
if not exist data mkdir data
echo Data directory ready!
echo.

REM Step 4: Display instructions and launch
echo [4/4] Launching application...
echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo The application will now start. You will see TWO windows:
echo   1. Backend server (intelligence engine)
echo   2. A new terminal for the frontend
echo.
echo Once both are running, open your browser to:
echo   http://localhost:8000/index.html
echo.
echo Press any key to continue...
echo.
pause

REM Launch backend in this window
cls
echo Starting backend server on http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server.
echo.

python backend.py

pause
