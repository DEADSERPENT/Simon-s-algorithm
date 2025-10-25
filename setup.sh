#!/bin/bash

# Simon's Algorithm - Automated Setup Script for Linux/macOS
# This script creates a virtual environment and installs all dependencies

echo "================================================================================"
echo "Simon's Algorithm - Automated Setup"
echo "================================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/6] Python detected"
python3 --version
echo ""

# Check if venv already exists
if [ -d "venv" ]; then
    echo "[WARNING] Virtual environment already exists!"
    read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    echo "Removing old virtual environment..."
    rm -rf venv
fi

echo "[2/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created successfully!"
echo ""

echo "[3/6] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo ""

echo "[4/6] Upgrading pip..."
python -m pip install --upgrade pip
echo ""

echo "[5/6] Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found, installing manually..."
    pip install qiskit qiskit-aer numpy scipy matplotlib
fi
echo ""

echo "[6/6] Verifying installation..."
python -c "import qiskit; print('Qiskit version:', qiskit.__version__)"
python -c "import qiskit_aer; print('Qiskit Aer installed successfully')"
python -c "import numpy; print('NumPy version:', numpy.__version__)"
echo ""

echo "================================================================================"
echo "Setup Complete!"
echo "================================================================================"
echo ""
echo "To run Simon's Algorithm:"
echo "  1. Activate the virtual environment:  source venv/bin/activate"
echo "  2. Run the program:                   python simon_qiskit.py"
echo "  3. Deactivate when done:              deactivate"
echo ""

read -p "Do you want to run the test suite now? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Setup complete. Run 'python simon_qiskit.py' when ready."
    exit 0
fi

echo ""
echo "================================================================================"
echo "Running Simon's Algorithm Test Suite"
echo "================================================================================"
echo ""
python simon_qiskit.py

echo ""
echo "================================================================================"
echo "Test suite completed!"
echo "================================================================================"
