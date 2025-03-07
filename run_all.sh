#!/bin/bash
set -e

# Determine which pip command to use
if command -v pip >/dev/null 2>&1; then
    PIP=pip
else
    PIP=pip3
fi

# Install Python dependencies
echo "Installing Python dependencies..."
$PIP install -r ./backend/requirements.txt

# Train the model
echo "Training model..."
ls ./backend/src
cd backend
# python -m src.train
cd ..

# Start the Python API in the background and disown it
echo "Starting Python API..."
$PIP install --upgrade typing-extensions
python ./backend/src/api.py & 
disown

# Change to the Angular dashboard directory, install node modules (if needed), then start the dashboard
echo "Starting Angular dashboard..."
cd frontend/dashboard
npm install 
ng serve