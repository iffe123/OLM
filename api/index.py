"""
Vercel serverless function handler
"""
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

# Export the FastAPI app for Vercel
handler = app
