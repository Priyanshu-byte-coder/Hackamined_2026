#!/bin/bash
echo "Starting SolarWatch Inference Server..."

if [ ! -f ".venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found. Please run ./setup_env.sh first!"
    exit 1
fi

source .venv/bin/activate
export ML_PORT=${ML_PORT:-8001}
echo "Starting on port $ML_PORT..."
uvicorn main:app --host 0.0.0.0 --port "$ML_PORT" --reload
