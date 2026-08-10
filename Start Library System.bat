@echo off
title Library Management System
cd /d "%~dp0"

echo ========================================
echo   Library Management System
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not added to PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

echo Installing / Updating required libraries...
echo This may take a minute the first time...
echo.

python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install requirements.
    echo Please check your internet connection and try again.
    pause
    exit /b
)

echo.
echo Libraries ready.
echo Starting the application...
echo.

python main.py

echo.
echo Application closed.
pause
