# Vercel Deployment Guide

## Changes Made to Fix FUNCTION_INVOCATION_FAILED Error

### 1. Added Vercel Configuration (`vercel.json`)
Created `vercel.json` to properly configure the Python serverless function with:
- Maximum execution time: 60 seconds (Pro plan)
- Memory allocation: 3008MB
- Proper routing to the FastAPI handler

### 2. File System Compatibility
**Changed**: All file operations now use `/tmp` directory
- **Before**: `uploads/` and `outputs/` directories in project root
- **After**: `/tmp/uploads` and `/tmp/outputs`
- **Why**: Vercel serverless functions only allow writes to `/tmp`

### 3. Error Handling Improvements
Added comprehensive try-catch blocks:
- File upload validation and error handling
- Static file serving with fallback paths
- Proper HTTP exception propagation
- Cleanup on errors

### 4. File Size Limits
Added 100MB upload limit to prevent timeouts:
- **Why**: Large files cause processing to exceed the 60-second limit
- **Solution**: Reject files > 100MB with helpful error message
- **Alternative**: Users can run the app locally for larger files

### 5. API Handler for Vercel
Created `api/index.py` as the entry point for Vercel's Python runtime

## Important Limitations on Vercel

### ⏱️ Timeout Constraints
- **Hobby Plan**: 10 seconds maximum
- **Pro Plan**: 60 seconds maximum
- Large OLM files may timeout - recommend local deployment for big files

### 📦 Request Size Limits
- **Hobby Plan**: 5MB maximum request body
- **Pro Plan**: 4.5GB maximum request body
- **Current Limit**: 100MB (configured to prevent timeouts)

### 💾 Storage
- `/tmp` storage is ephemeral (cleared between invocations)
- In-memory state (`conversion_status` dict) doesn't persist
- Files are lost when function scales to zero

### 🔄 Stateless Architecture
- Each request may hit a different function instance
- Background tasks might not complete if function terminates
- Consider using external storage (S3, R2) for production use

## Deployment Steps

### Option 1: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project directory
vercel

# For production deployment
vercel --prod
```

### Option 2: Deploy via GitHub Integration

1. Push code to GitHub
2. Connect repository to Vercel
3. Vercel auto-deploys on push

### Option 3: Deploy via Vercel Dashboard

1. Go to vercel.com
2. Click "Import Project"
3. Select this repository
4. Vercel auto-detects Python and deploys

## Environment Variables

No environment variables required for basic operation. All dependencies are in `requirements.txt`.

## Testing the Deployment

After deployment, test these endpoints:

1. **Root**: `GET /` - Should serve the HTML interface
2. **Upload**: `POST /api/upload` - Upload a small .olm file
3. **Status**: `GET /api/status/{task_id}` - Check processing status
4. **Download**: `GET /api/download/{task_id}/{format}` - Download results

## Monitoring

Check Vercel logs for errors:
```bash
vercel logs
```

Common issues:
- **Timeout errors**: File too large or processing took > 60s
- **Memory errors**: File extraction exceeded 3GB memory limit
- **Path errors**: Static files not found (check build output)

## Local Development

For testing without Vercel:

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Or with uvicorn
uvicorn app:app --reload --port 8000
```

## Production Recommendations

For production use with large files:

1. **Use external storage**: AWS S3, Cloudflare R2, or similar
2. **Implement queue system**: For long-running conversions
3. **Add database**: PostgreSQL/MySQL for persistent state
4. **Consider alternatives**: Railway, Render, or DigitalOcean for long-running processes

## Architecture Comparison

| Feature | Current (Serverless) | Recommended (Production) |
|---------|---------------------|--------------------------|
| File Storage | `/tmp` (ephemeral) | S3/R2 (persistent) |
| State Tracking | In-memory dict | Database (PostgreSQL) |
| Processing | Synchronous/Background | Queue (Celery/Bull) |
| Timeout | 60 seconds | Unlimited |
| Scalability | Auto-scales | Manual/Auto-scale |
| Cost | Pay-per-invocation | Fixed monthly |

## Troubleshooting

### FUNCTION_INVOCATION_FAILED

**Symptoms**: 500 error, function crashes

**Common Causes**:
1. **Timeout**: Processing exceeded 60 seconds
   - Solution: Reduce file size or run locally
2. **Memory**: File extraction exceeded 3GB
   - Solution: Reduce file size
3. **Unhandled exception**: Code threw an error
   - Solution: Check Vercel logs for stack trace
4. **Missing dependencies**: Library not in requirements.txt
   - Solution: Add to requirements.txt and redeploy

### Static Files Not Loading

**Symptoms**: 404 on root path or styles missing

**Solution**: Ensure `static/` directory is included in deployment
- Check `.vercelignore` doesn't exclude it
- Verify path resolution in `app.py:137-148`

### Background Tasks Not Completing

**Symptoms**: Status stuck at "processing"

**Cause**: Function terminated before background task finished

**Solution**:
- Reduce file size
- Consider synchronous processing
- Use external queue system

## Cost Estimation

### Vercel Pricing
- **Hobby**: Free tier, limited usage
- **Pro**: $20/month, includes:
  - 60s function timeout
  - 4.5GB request size
  - Higher usage limits

### Recommendations
- **Small files (< 10MB)**: Hobby plan works
- **Medium files (10-100MB)**: Pro plan recommended
- **Large files (> 100MB)**: Use dedicated hosting
