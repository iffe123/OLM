@echo off
title OLM File Converter
echo ============================================
echo        OLM File Converter
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check the box that says
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python... OK
echo.

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/3] Setting up for first time use...
    echo       This may take a minute...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
) else (
    echo [2/3] Loading application...
    call venv\Scripts\activate.bat
)

echo.
echo [3/3] Starting OLM File Converter...
echo.
echo ============================================
echo   The app is now running!
echo
echo   Open your browser to: http://localhost:8000
echo
echo   To stop the app, close this window
echo   or press Ctrl+C
echo ============================================
echo.

:: Open browser after a short delay
start "" "http://localhost:8000"

:: Run the app
python app.py

pause
