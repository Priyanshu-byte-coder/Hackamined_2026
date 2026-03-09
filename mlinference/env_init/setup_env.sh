#!/bin/bash
echo "=============================================="
echo "SolarWatch Inference Server Setup (Mac/Linux)"
echo "=============================================="

echo "[1/3] Creating virtual environment (.venv)..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment. Ensure python3-venv is installed."
    exit 1
fi

echo "[2/3] Activating virtual environment..."
source .venv/bin/activate

echo "[3/3] Installing requirements..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo "To start the server, run:"
echo "  1. source .venv/bin/activate"
echo "  2. python main.py"
echo ""
echo "(Or just run ./start_server.sh)"
