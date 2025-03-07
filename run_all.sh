#!/bin/bash
set -e

# Check if pip is installed
if ! command -v pip >/dev/null 2>&1; then
    echo "pip not found. Installing pip..."
    python -m ensurepip --upgrade
else
    echo "pip found: $(pip --version)"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r ./backend/requirements.txt

# Train the model
echo "Training model..."
ls ./backend/src
cd backend
python -m src.train
cd ..

# Start the Python API in the background and disown it
echo "Starting Python API..."
pip install --upgrade typing-extensions
python ./backend/src/api.py & 
disown

# Change to the Angular dashboard directory, install node modules (if needed), then start the dashboard
echo "Starting Angular dashboard..."
cd frontend/dashboard
npm install 
ng serve