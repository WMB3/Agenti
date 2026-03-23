@echo off
setlocal enabledelayedexpansion
title E-Bid Intelligence Local Startup

echo ===================================================
echo   E-BID INTELLIGENCE SYSTEM STARTUP (Pure Batch)
echo ===================================================
echo.

:: 1. Check Python or Py (Python Launcher)
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)

if "!PYTHON_CMD!"=="" (
    echo [ERROR] Python was not found on your system PATH.
    echo.
    echo To fix this:
    echo 1. Re-install Python from python.org
    echo 2. During installation, CHECK the box that says "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo [OK] Python detected as "!PYTHON_CMD!".

:: 2. Check NPM
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM not found! Please install Node.js and add it to your PATH.
    pause
    exit /b 1
)
echo [OK] NPM detected.

:: 3. Setup Backend .env
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from template...
    echo GEMINI_API_KEY=your_key_here > "backend\.env"
    echo MODEL_ID=gemini-1.5-flash >> "backend\.env"
)

:: 4. Install Backend Requirements
echo [INFO] Ensuring Python dependencies are installed...
!PYTHON_CMD! -m pip install -r backend/requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install Python dependencies. Please check your internet connection.
)

:: 5. Setup Frontend node_modules
if not exist "nexus-terminal\node_modules\" (
    echo [INFO] nexus-terminal\node_modules not found. Installing dependencies...
    pushd nexus-terminal
    call npm install --silent
    popd
)

:: 6. Launch Services
echo [INFO] Launching Services...

:: Start Backend
start "E-Bid Backend" cmd /k "cd backend && !PYTHON_CMD! main.py"

:: Start Frontend
start "E-Bid Frontend" cmd /k "cd nexus-terminal && npm run dev"

echo.
echo ===================================================
echo SYSTEM ONLINE.
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ===================================================
echo.
echo Press any key to close this launcher...
pause >nul
exit /b 0
