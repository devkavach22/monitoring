@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo      ScreenShort: Automatic Setup ^& Runner
echo ====================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed.
    echo Please install Python 3.x and ensure 'Add Python to PATH' is checked.
    pause
    exit /b
)

:: 2. Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating virtual environment (venv)...
    python -m venv venv
)

:: 3. Activate venv and install dependencies
echo [*] Activating environment and verifying dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet

:: 4. Ensure .env exists (Warn if missing)
if not exist ".env" (
    echo [!] WARNING: .env file not found. 
    echo Please copy .env.example to .env and fill in your server details.
    if exist ".env.example" (
        copy .env.example .env
        echo [*] Created .env from .env.example. Please edit it before next run.
    )
)

:: 5. Run the application
echo [*] Launching ScreenShort...
echo [Keep this window open to continue capturing]
python main.py

if %errorlevel% neq 0 (
    echo [!] Program exited with an error.
    pause
)
pause
