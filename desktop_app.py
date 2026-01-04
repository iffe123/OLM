#!/usr/bin/env python3
"""
OLM File Converter - Desktop Application
Double-click to run, opens browser automatically
"""

import sys
import os
import webbrowser
import threading
import time
import signal

# Ensure we can find our modules when running as executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = os.path.dirname(sys.executable)
    os.chdir(app_dir)
else:
    # Running as script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

# Now import our app
import uvicorn
from app import app

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def open_browser():
    """Open browser after short delay to let server start"""
    time.sleep(1.5)
    print(f"\nOpening browser at {URL}")
    webbrowser.open(URL)


def main():
    print("=" * 50)
    print("   OLM File Converter - Desktop Edition")
    print("=" * 50)
    print()
    print(f"Starting server at {URL}")
    print()
    print("The app will open in your browser automatically.")
    print("Keep this window open while using the app.")
    print()
    print("Press Ctrl+C to quit")
    print("=" * 50)

    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Run the server
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="warning",
            access_log=False
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
