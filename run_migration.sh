#!/bin/bash

echo "============================================================"
echo "Snaplove MongoDB to MySQL Migration Tool"
echo "============================================================"
echo

echo "[0/4] Checking configuration file..."
if [ ! -f "config.py" ]; then
    if [ -f "config.example.py" ]; then
        echo "WARNING: config.py not found. Creating from template..."
        cp config.example.py config.py
        echo
        echo "Please edit config.py and update MySQL credentials before continuing!"
        echo
        exit 1
    else
        echo "ERROR: config.example.py not found"
        exit 1
    fi
fi
echo "Config file found."
echo

echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ first"
    exit 1
fi
python3 --version
echo

echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo

echo "[3/4] Running connection test..."
python3 test_connection.py
if [ $? -ne 0 ]; then
    echo
    echo "Please fix the issues above before running migration."
    exit 1
fi
echo

echo "============================================================"
echo "Ready to migrate!"
echo "============================================================"
echo
read -p "Do you want to start migration now? (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo
    echo "Starting migration..."
    echo
    python3 converter.py
    echo
    echo "============================================================"
    echo "Migration process completed!"
    echo "============================================================"
else
    echo
    echo "Migration cancelled. Run 'python3 converter.py' when ready."
fi
echo
