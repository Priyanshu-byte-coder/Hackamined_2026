@echo off
echo Starting SolarWatch Inference Server...

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run setup_env.bat first!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python main.py
pause
