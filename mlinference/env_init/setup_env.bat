@echo off
echo ==============================================
echo SolarWatch Inference Server Setup (Windows)
echo ==============================================

echo [1/3] Creating virtual environment (.venv)...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment. Ensure Python is installed and in your PATH.
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/3] Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==============================================
echo Setup Complete!
echo ==============================================
echo To start the server, run:
echo   1. call .venv\Scripts\activate.bat
echo   2. python main.py
echo.
echo (Or just run start_server.bat)
pause
