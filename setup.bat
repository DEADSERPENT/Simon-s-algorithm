@echo off
REM Simon's Algorithm - Automated Setup Script for Windows
REM This script creates a virtual environment and installs all dependencies

echo ================================================================================
echo Simon's Algorithm - Automated Setup
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python detected
python --version
echo.

REM Check if venv already exists
if exist "venv\" (
    echo [WARNING] Virtual environment already exists!
    echo.
    choice /C YN /M "Do you want to delete and recreate it"
    if errorlevel 2 (
        echo Setup cancelled.
        pause
        exit /b 0
    )
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo [2/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [5/6] Installing project dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found, installing manually...
    pip install qiskit qiskit-aer numpy scipy matplotlib
)
echo.

echo [6/6] Verifying installation...
python -c "import qiskit; print('Qiskit version:', qiskit.__version__)"
python -c "import qiskit_aer; print('Qiskit Aer installed successfully')"
python -c "import numpy; print('NumPy version:', numpy.__version__)"
echo.

echo ================================================================================
echo Setup Complete!
echo ================================================================================
echo.
echo To run Simon's Algorithm:
echo   1. Activate the virtual environment:  venv\Scripts\activate
echo   2. Run the program:                   python simon_qiskit.py
echo   3. Deactivate when done:              deactivate
echo.
echo To run now, type: python simon_qiskit.py
echo.

choice /C YN /M "Do you want to run the test suite now"
if errorlevel 2 (
    echo.
    echo Setup complete. Run 'python simon_qiskit.py' when ready.
    pause
    exit /b 0
)

echo.
echo ================================================================================
echo Running Simon's Algorithm Test Suite
echo ================================================================================
echo.
python simon_qiskit.py

echo.
echo ================================================================================
echo Test suite completed!
echo ================================================================================
pause
