#!/bin/bash
set -e

# Check if Homebrew is installed; if not, install it
if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "Homebrew is installed: $(brew --version)"
fi

# Check if pyenv is installed; if not, install it using Homebrew.
if ! command -v pyenv >/dev/null 2>&1; then
    echo "pyenv not found. Installing pyenv via Homebrew..."
    brew update && brew install pyenv
else
    echo "pyenv is installed: $(pyenv --version)"
fi

# Enable pyenv shell integration
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Check if Python 3.10.12 is installed via pyenv; if not, install it.
if ! pyenv versions --bare | grep -qx "3.10.12"; then
  echo "Python 3.10.12 not installed. Installing via pyenv..."
  pyenv install 3.10.12
fi

# Set pyenv shell to Python 3.10.12 so that the correct Python is used.
pyenv shell 3.10.12

# Define which Python to use. With pyenv set, "python" should now point to 3.10.12.
PYTHON=python

# Check if the specified Python is installed
if ! command -v $PYTHON >/dev/null 2>&1; then
    echo "$PYTHON not found. Please install Python 3.10."
    exit 1
else
    echo "Using $PYTHON: $($PYTHON --version)"
fi

# Use the chosen Python's pip to install dependencies.
echo "Installing Python dependencies..."
$PYTHON -m ensurepip --upgrade
$PYTHON -m pip install -r ./backend/requirements.txt

# Train the model
echo "Training model..."
ls ./backend/src
cd backend
# Uncomment the following line if you want to run training:
# $PYTHON -m src.train
cd ..

# Start the Python API in the background and disown it
echo "Starting Python API..."
$PYTHON -m pip install --upgrade typing-extensions
$PYTHON ./backend/src/api.py &
disown

# Change to the Angular dashboard directory, install node modules if needed, then start the dashboard
echo "Starting Angular dashboard..."
cd frontend/dashboard
npm install
ng serve