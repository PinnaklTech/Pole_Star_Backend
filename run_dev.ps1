# Development server startup script for Windows
Write-Host "Starting Pole Star Backend Server..." -ForegroundColor Green
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot

# Run uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

