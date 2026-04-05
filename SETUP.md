# DevFix Auto-Agent Setup Guide

## Fixed Issues ✅
1. **Replaced deprecated Docker SDK** - Now using subprocess directly with Docker CLI
2. **Added requirements.txt** - Proper dependency management
3. **Fixed import issues** - All imports verified and working
4. **Added environment setup** - .env.example file for Google API key

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

Get your Google API key from: https://makersuite.google.com/app/apikey

### 3. Ensure Docker is Running
```bash
docker --version
docker ps
```

If Docker is not running, start Docker Desktop.

### 4. Run the Project
```bash
python main.py --task "Create a function that adds two numbers and test it"
```

## Requirements
- Python 3.10+ (currently using 3.9 - should upgrade)
- Docker Desktop running
- Google API key

## Testing
All syntax checks pass ✅
All imports work correctly ✅
Graph compilation successful ✅

## Configuration Notes
- Model uses `gemini-2.5-flash` (stable, widely supported)
- Ensure .env file format: `GOOGLE_API_KEY=your_key` (no spaces around =)
- Docker must be running for code execution

## Known Warnings (Non-Critical)
- Python 3.9 is EOL (upgrade recommended)
- OpenSSL warnings (can be ignored)
- Google libraries recommend Python 3.10+