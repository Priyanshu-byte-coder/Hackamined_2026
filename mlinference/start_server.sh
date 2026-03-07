#!/bin/bash
echo "Starting SolarWatch Inference Server..."

if [ ! -f ".venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found. Please run ./setup_env.sh first!"
    exit 1
fi

source .venv/bin/activate
python main.py
