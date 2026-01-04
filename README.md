# OLM File Converter

A powerful tool to convert Outlook for Mac (.olm) files into Claude-friendly formats. Extract emails from OLM archives and convert them to CSV, TXT, JSON, PDF, or Markdown formats.

## Features

- **Large File Support**: No size limits when running locally (desktop app)
- **Multiple Output Formats**:
  - 📊 **CSV** - Perfect for spreadsheet analysis and data processing
  - 📄 **TXT** - Plain text format, ideal for sharing with Claude AI
  - 🔧 **JSON** - Structured data for programming and API integration
  - 📑 **PDF** - Professional document format for archiving
  - 📝 **MD** - Markdown format, perfect for documentation and Google Drive
- **Fast Processing**: Chunked file uploads and efficient parsing
- **Progress Tracking**: Real-time status updates during conversion
- **User-Friendly Interface**: Drag-and-drop file upload
- **Batch Conversion**: Convert to multiple formats simultaneously

## Installation

### Option 1: Desktop App (Recommended for Large Files)

Build a standalone executable that runs locally with **no file size limits**:

**Quick Start (requires Python 3.8+):**
```bash
# Clone the repository
git clone <repository-url>
cd OLM

# Build the desktop app
python build_app.py
```

This creates `OLM-Converter` (or `OLM-Converter.exe` on Windows) in the `dist/` folder. Double-click to run - your browser opens automatically!

**Or run directly without building:**

**Windows:** Double-click `start.bat`

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Web Deployment (Vercel)

Deploy to Vercel for web access. Note: Vercel has upload limits (4.5MB free, 100MB Pro). For files larger than this, use the Desktop App option above.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Manual Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd OLM
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The application will start at `http://localhost:8000`

### Converting OLM Files

1. **Open your browser** and navigate to `http://localhost:8000`

2. **Upload your OLM file**:
   - Click the upload area or drag & drop your .olm file
   - No size limit when running locally

3. **Select output formats**:
   - Choose one or more formats: CSV, TXT, JSON, PDF, MD
   - Multiple formats can be selected for a single conversion

4. **Click "Convert File"**:
   - Monitor the progress bar
   - Wait for processing to complete

5. **Download your files**:
   - Click download buttons for each format
   - Files are ready to use with Claude or other tools

### Using Converted Files with Claude

The converted files are optimized for use with Claude AI:

- **TXT files**: Can be directly uploaded to Claude for analysis, summarization, or Q&A
- **CSV files**: Upload for data analysis, insights, or to generate reports
- **JSON files**: Use for structured queries or programmatic access
- **PDF files**: Share as formatted documents or for archival purposes
- **MD files**: Upload to Google Drive or use for documentation - perfectly formatted for readability

## API Endpoints

The application provides a REST API for programmatic access:

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: OLM file
- formats: Comma-separated list (e.g., "csv,txt,json,md")

Response:
{
  "task_id": "20240104_123456_789",
  "message": "File uploaded successfully",
  "formats": ["csv", "txt", "json"]
}
```

### Check Status
```bash
GET /api/status/{task_id}

Response:
{
  "status": "completed",
  "progress": 100,
  "message": "Successfully converted 150 emails",
  "email_count": 150,
  "files": [
    {
      "format": "csv",
      "filename": "20240104_123456_789.csv",
      "size": 45678
    }
  ]
}
```

### Download File
```bash
GET /api/download/{task_id}/{format}

Returns: File download
```

### Cleanup
```bash
DELETE /api/cleanup/{task_id}

Response:
{
  "message": "Cleanup completed"
}
```

## Technical Details

### OLM File Format

OLM (Outlook for Mac) files are structured archives containing:
- Email messages in .eml format (RFC 822)
- XML metadata files
- Attachments and embedded content
- Folder structure information

### Parsing Strategy

The converter uses multiple parsing strategies:
1. **Primary**: Extracts .eml files using Python's email library
2. **Secondary**: Parses XML message files for alternative formats
3. **Fallback**: Text extraction for edge cases

### Output Formats

**CSV Format**:
- Columns: Date, From, To, CC, Subject, Body, Attachments
- Compatible with Excel, Google Sheets, pandas
- Ideal for data analysis and filtering

**TXT Format**:
- Readable plain text with clear separators
- Each email formatted as a distinct section
- Perfect for Claude AI conversations

**JSON Format**:
- Structured data with full metadata
- ISO-formatted timestamps
- Easy to parse programmatically

**PDF Format**:
- Professional document layout
- Each email on separate page
- Suitable for archiving and sharing

**MD (Markdown) Format**:
- Clean, readable markdown formatting
- Email metadata in table format
- Perfect for Google Drive and documentation
- Easy to share and collaborate on

## Configuration

### File Size Limits

The default maximum file size is 10GB. To change this, modify `app.py`:

```python
# Add to FastAPI app configuration
app = FastAPI()
app.add_middleware(
    # ... other middleware
)
# Adjust MAX_UPLOAD_SIZE as needed
```

### Temporary File Cleanup

Files older than 1 hour are automatically deleted. Adjust in `app.py`:

```python
def cleanup_old_files():
    # Change 3600 (1 hour) to your preferred value
    if file_age > 3600:  # seconds
        file_path.unlink()
```

## Troubleshooting

### "Failed to parse OLM file"
- Ensure the file is a valid .olm archive
- Check that the file isn't corrupted
- Try extracting the .olm manually to verify contents

### "No emails found"
- The OLM file might be empty
- Try a different OLM file
- Check if the file is actually an OLM format

### Upload timeout for large files
- Increase server timeout settings
- Check your network connection
- Try smaller files first to test

### Memory issues with large files
- Ensure sufficient RAM available
- Close other applications
- Process smaller OLM files in batches

## Security Notes

- Files are processed locally on your server
- Temporary files are automatically cleaned up
- No data is sent to external services
- All processing happens on your machine

## Development

### Project Structure
```
OLM/
├── app.py                 # FastAPI application
├── olm_parser.py         # OLM file parsing logic
├── format_converters.py  # Format conversion functions
├── requirements.txt      # Python dependencies
├── static/
│   └── index.html       # Web interface
├── uploads/             # Temporary upload storage
└── outputs/             # Converted file storage
```

### Adding New Formats

To add a new output format:

1. Create converter function in `format_converters.py`:
```python
def convert_to_newformat(emails: List[Dict], output_path: Path):
    # Your conversion logic
    pass
```

2. Add to processing in `app.py`:
```python
elif fmt == "newformat":
    await asyncio.to_thread(convert_to_newformat, emails, output_path)
```

3. Update frontend in `static/index.html`

## License

This project is open source and available for personal and commercial use.

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Changelog

### Version 1.2.0
- Added standalone desktop app support (PyInstaller)
- Auto-open browser on start
- Fixed Vercel deployment configuration

### Version 1.1.0
- Added Markdown (MD) format support
- Enhanced documentation

### Version 1.0.0
- Initial release
- Support for CSV, TXT, JSON, and PDF formats
- Web-based interface
- Large file handling
- Progress tracking
- Automatic cleanup