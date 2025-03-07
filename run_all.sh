#!/bin/bash
set -e

# Enable pyenv shell integration
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi

# Set pyenv shell to Python 3.10.12 so that the correct python is used
pyenv shell 3.10.12

# Define which Python version to use. With pyenv set, "python" now points to 3.10.12.
PYTHON=python

# Check if the specified Python is installed
if ! command -v $PYTHON >/dev/null 2>&1; then
    echo "$PYTHON not found. Please install Python 3.10."
    exit 1
else
    echo "Using $PYTHON: $($PYTHON --version)"
fi

# Use the chosen Python's pip to install dependencies
echo "Installing Python dependencies..."
$PYTHON -m ensurepip --upgrade
$PYTHON -m pip install -r ./backend/requirements.txt

# Train the model
echo "Training model..."
ls ./backend/src
cd backend
# Uncomment the following line if you want to run training
# $PYTHON -m src.train
cd ..

# Start the Python API in the background and disown it
echo "Starting Python API..."
$PYTHON -m pip install --upgrade typing-extensions
$PYTHON ./backend/src/api.py &
disown

# Change to the Angular dashboard directory, install node modules (if needed), then start the dashboard
echo "Starting Angular dashboard..."
cd frontend/dashboard
npm install
ng serve