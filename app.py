"""
OLM File Converter - FastAPI Application
Converts OLM files to CSV, TXT, JSON, and PDF formats
"""
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from olm_parser import OLMParser
from format_converters import (
    convert_to_csv,
    convert_to_txt,
    convert_to_json,
    convert_to_pdf,
    convert_to_md
)

app = FastAPI(title="OLM File Converter", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories - Use /tmp for serverless environments
UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Store conversion status
conversion_status = {}


def cleanup_old_files():
    """Remove files older than 1 hour"""
    current_time = datetime.now().timestamp()
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 3600:  # 1 hour
                    file_path.unlink()


async def process_olm_file(
    file_path: Path,
    task_id: str,
    output_formats: List[str]
):
    """Process OLM file and convert to requested formats"""
    try:
        # Ensure directories exist
        UPLOAD_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

        conversion_status[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Extracting OLM file..."
        }

        # Parse OLM file
        parser = OLMParser(file_path)
        conversion_status[task_id]["progress"] = 20
        conversion_status[task_id]["message"] = "Parsing emails..."

        emails = await asyncio.to_thread(parser.parse)

        if not emails:
            conversion_status[task_id] = {
                "status": "error",
                "message": "No emails found in OLM file"
            }
            return

        conversion_status[task_id]["progress"] = 50
        conversion_status[task_id]["message"] = f"Found {len(emails)} emails. Converting..."

        # Convert to requested formats
        output_files = []
        progress_per_format = 50 / len(output_formats)

        for idx, fmt in enumerate(output_formats):
            output_path = OUTPUT_DIR / f"{task_id}.{fmt}"

            if fmt == "csv":
                await asyncio.to_thread(convert_to_csv, emails, output_path)
            elif fmt == "txt":
                await asyncio.to_thread(convert_to_txt, emails, output_path)
            elif fmt == "json":
                await asyncio.to_thread(convert_to_json, emails, output_path)
            elif fmt == "pdf":
                await asyncio.to_thread(convert_to_pdf, emails, output_path)
            elif fmt == "md":
                await asyncio.to_thread(convert_to_md, emails, output_path)

            output_files.append({
                "format": fmt,
                "filename": f"{task_id}.{fmt}",
                "size": output_path.stat().st_size
            })

            conversion_status[task_id]["progress"] = 50 + int((idx + 1) * progress_per_format)

        conversion_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": f"Successfully converted {len(emails)} emails",
            "email_count": len(emails),
            "files": output_files
        }

        # Cleanup
        parser.cleanup()
        if file_path.exists():
            file_path.unlink()

    except Exception as e:
        conversion_status[task_id] = {
            "status": "error",
            "message": str(e)
        }
        if file_path.exists():
            file_path.unlink()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        # Try multiple paths for different deployment environments
        html_paths = [
            Path("static/index.html"),
            Path(__file__).parent / "static" / "index.html",
            Path("/var/task/static/index.html")
        ]

        for html_path in html_paths:
            if html_path.exists():
                with open(html_path, "r") as f:
                    return f.read()

        # If no HTML file found, return a simple page
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OLM File Converter API</title>
        </head>
        <body>
            <h1>OLM File Converter API</h1>
            <p>API is running. Visit the <a href="/docs">/docs</a> endpoint for API documentation.</p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OLM File Converter API</title>
        </head>
        <body>
            <h1>OLM File Converter API</h1>
            <p>API is running. Visit the <a href="/docs">/docs</a> endpoint for API documentation.</p>
            <p><small>Error loading UI: {str(e)}</small></p>
        </body>
        </html>
        """


@app.post("/api/upload")
async def upload_olm(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    formats: str = "csv,txt,json"
):
    """
    Upload OLM file and start conversion

    Args:
        file: OLM file (up to 100MB on Vercel)
        formats: Comma-separated list of output formats (csv,txt,json,pdf,md)
    """
    # Validate file
    if not file.filename.lower().endswith('.olm'):
        raise HTTPException(400, "Only .olm files are supported")

    # Parse requested formats
    output_formats = [f.strip().lower() for f in formats.split(",")]
    valid_formats = {"csv", "txt", "json", "pdf", "md"}
    output_formats = [f for f in output_formats if f in valid_formats]

    if not output_formats:
        raise HTTPException(400, "No valid output formats specified")

    # Generate task ID
    task_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = UPLOAD_DIR / f"{task_id}.olm"

    # Save uploaded file
    try:
        # Ensure directories exist
        UPLOAD_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Validate file
        if not file.filename:
            raise HTTPException(400, "No file provided")

        if not file.filename.lower().endswith('.olm'):
            raise HTTPException(400, "Only .olm files are supported")

        # Parse requested formats
        output_formats = [f.strip().lower() for f in formats.split(",")]
        valid_formats = {"csv", "txt", "json", "pdf"}
        output_formats = [f for f in output_formats if f in valid_formats]

        if not output_formats:
            raise HTTPException(400, "No valid output formats specified")

        # Generate task ID
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_path = UPLOAD_DIR / f"{task_id}.olm"

        # Save uploaded file with size tracking
        try:
            total_size = 0
            # Vercel Pro limit is 4.5GB, but we should limit smaller for safety
            max_size = 100 * 1024 * 1024  # 100MB limit to prevent timeouts

            with open(file_path, "wb") as buffer:
                # Read in chunks for large files
                while chunk := await file.read(1024 * 1024 * 10):  # 10MB chunks
                    total_size += len(chunk)
                    if total_size > max_size:
                        buffer.close()
                        if file_path.exists():
                            file_path.unlink()
                        raise HTTPException(
                            413,
                            f"File too large. Maximum size is {max_size // (1024*1024)}MB for serverless processing. "
                            "For larger files, consider running this application locally."
                        )
                    buffer.write(chunk)

        except HTTPException:
            raise
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(500, f"Failed to save file: {str(e)}")

        # Start background processing
        background_tasks.add_task(process_olm_file, file_path, task_id, output_formats)

        # Cleanup old files
        background_tasks.add_task(cleanup_old_files)

        return {
            "task_id": task_id,
            "message": "File uploaded successfully. Processing started.",
            "formats": output_formats
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get conversion status"""
    if task_id not in conversion_status:
        raise HTTPException(404, "Task not found")

    return conversion_status[task_id]


@app.get("/api/download/{task_id}/{format}")
async def download_file(task_id: str, format: str):
    """Download converted file"""
    try:
        file_path = OUTPUT_DIR / f"{task_id}.{format}"

        if not file_path.exists():
            raise HTTPException(404, "File not found or has been cleaned up")

        return FileResponse(
            path=file_path,
            filename=f"converted_emails.{format}",
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to download file: {str(e)}")


@app.delete("/api/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """Clean up task files"""
    # Remove output files
    for ext in ["csv", "txt", "json", "pdf", "md"]:
        file_path = OUTPUT_DIR / f"{task_id}.{ext}"
        if file_path.exists():
            file_path.unlink()

    # Remove from status
    if task_id in conversion_status:
        del conversion_status[task_id]

    return {"message": "Cleanup completed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
