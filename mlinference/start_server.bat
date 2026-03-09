@echo off
echo Starting SolarWatch Inference Server...

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run setup_env.bat first!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
set ML_PORT=8001
echo Starting on port %ML_PORT%...
uvicorn main:app --host 0.0.0.0 --port %ML_PORT% --reload
pause
