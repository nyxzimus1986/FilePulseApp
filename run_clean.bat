@echo off
REM FilePulse Clean Launcher for Windows
REM Fast startup without splash screen animations

echo Starting FilePulse (Clean Mode)...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the clean launcher
python filepulseapp.py %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)
