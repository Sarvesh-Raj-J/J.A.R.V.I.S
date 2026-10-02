@echo off
REM Jarvis Launcher Script for Windows
REM Double-click this file to start Jarvis

echo ========================================
echo       Starting Jarvis Assistant
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist config.json (
    echo Configuration file not found!
    echo Running setup wizard...
    echo.
    python setup_wizard.py
    echo.
    echo Setup complete! Starting Jarvis...
    echo.
)

REM Check for command line arguments
if "%1"=="--console" (
    echo Starting Jarvis in console mode...
    python jarvis_main.py
) else (
    echo Starting Jarvis with Futuristic UI...
    echo.
    python jarvis_futuristic_ui.py
)

REM Pause on error
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Jarvis encountered an error
    echo   Check jarvis.log for details
    echo ========================================
    pause
)
