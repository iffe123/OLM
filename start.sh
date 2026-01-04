#!/bin/bash

# OLM File Converter - Start Script

echo "================================"
echo "OLM File Converter - Starting..."
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "Dependencies installed successfully!"
echo ""

# Create necessary directories
mkdir -p uploads outputs

echo "================================"
echo "Starting OLM File Converter..."
echo "================================"
echo ""
echo "Server will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py
