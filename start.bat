@echo off
REM OLM File Converter - Start Script for Windows

echo ================================
echo OLM File Converter - Starting...
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed successfully!
echo.

REM Create necessary directories
if not exist "uploads\" mkdir uploads
if not exist "outputs\" mkdir outputs

echo ================================
echo Starting OLM File Converter...
echo ================================
echo.
echo Server will be available at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py
