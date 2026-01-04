#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

echo "============================================"
echo "       OLM File Converter"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python:"
    echo ""
    echo "  Option 1: Download from https://www.python.org/downloads/"
    echo ""
    echo "  Option 2 (Mac): Install with Homebrew:"
    echo "    brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/3] Checking Python... OK"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/3] Setting up for first time use..."
    echo "      This may take a minute..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
else
    echo "[2/3] Loading application..."
    source venv/bin/activate
fi

echo ""
echo "[3/3] Starting OLM File Converter..."
echo ""
echo "============================================"
echo "  The app is now running!"
echo ""
echo "  Open your browser to: http://localhost:8000"
echo ""
echo "  To stop the app, close this window"
echo "  or press Ctrl+C"
echo "============================================"
echo ""

# Open browser after a short delay (works on Mac)
sleep 2
if command -v open &> /dev/null; then
    open "http://localhost:8000"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8000"
fi

# Run the app
python3 app.py
