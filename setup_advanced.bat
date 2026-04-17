@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo      ScreenShort: OPTIMIZED SETUP ^& INSTALLER
echo ====================================================

:: 1. Check for uv (Faster than pip)
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%PATH%;%USERPROFILE%\.cargo\bin"
)

:: 1.5. Ensure Python version is installed
echo [*] Ensuring required Python version is installed...
uv python install

:: 2. Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [!] .env file missing. Creating from .env.example...
        copy .env.example .env
        echo [!] PLEASE EDIT .env WITH YOUR CREDENTIALS.
    )
)

:: 3. Setup Virtual Environment and Install Dependencies
echo [*] Syncing dependencies using uv...
uv sync

:: 4. Run main.py immediately
echo [*] Launching ScreenShort via uv...
uv run main.py

:: 5. Optional: Build the EXE
set /p build_exe="Do you want to build the standalone EXE and add to startup? (y/n): "
if /i "%build_exe%"=="y" (
    :: Clean previous builds
    if exist "dist" rd /s /q "dist"
    if exist "build" rd /s /q "build"

    echo [*] Compiling ScreenShort into an optimized standalone EXE...
    uv run pyinstaller --noconfirm ScreenShort.spec

    if %errorlevel% eq 0 (
        set "EXE_PATH=%CD%\dist\ScreenShort.exe"
        set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

        echo [*] Adding ScreenShort to Windows Startup...
        powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTUP_FOLDER%\ScreenShort.lnk');$s.TargetPath='%EXE_PATH%';$s.WorkingDirectory='%CD%';$s.Save()"
        
        echo ====================================================
        echo      INSTALLATION COMPLETE (OPTIMIZED)
        echo ====================================================
        echo 1. Your EXE is located in: \dist\ScreenShort.exe
        echo 2. It will start automatically when you login.
    ) else (
        echo [!] ERROR: Compilation failed.
    )
)

pause
