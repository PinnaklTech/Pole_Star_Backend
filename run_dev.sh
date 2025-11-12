#!/bin/bash
# Development server startup script for Linux/Mac

echo "Starting Pole Star Backend Server..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Run uvicorn with auto-reload
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

