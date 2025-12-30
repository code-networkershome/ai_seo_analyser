@echo off
set "PATH=C:\Windows\System32;%PATH%"
echo ========================================
echo   Starting Backend Development Server
echo ========================================
echo.
echo IMPORTANT: Run this in a NEW terminal as Administrator
echo.
cd backend

:: Check if Python is installed and is version 3.12+
python --version 2>nul | find "Python 3.1" >nul
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python 3.12+ is required but not found!
    echo Please install Python 3.12+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to create virtual environment
        echo Please run this script as Administrator
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing/Updating Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Backend Server Starting...
echo   - Local:    http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo ========================================
echo.

echo [INFO] Starting Uvicorn server...
uvicorn main:app --reload --port 8000

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start the backend server
    echo Please check if port 8000 is available
    pause
    exit /b 1
)
