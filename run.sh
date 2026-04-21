#!/bin/bash

# LunaAura Bootstrapper Script
echo "🌙 Starting LunaAura Core Infrastructure..."

# 1. Clean up abandoned ports
echo "Checking for hanging background processes on Port 5001..."
if lsof -t -i:5001 > /dev/null
then
    echo "Killing rogue process blocking port 5001..."
    lsof -t -i:5001 | xargs kill -9
fi

# 2. Source the environment natively
if [ -d "venv" ]; then
    echo "Activating Virtual Environment..."
    source venv/bin/activate
else
    echo "Virtual Environment not found! Creating 'venv'..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install flask flask-cors pandas scikit-learn numpy joblib
fi

# 3. Boot Server in Foreground
echo "Booting Flask API Server natively (CTRL+C to terminate)..."
python api/app.py
