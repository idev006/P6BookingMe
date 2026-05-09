@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Environment Setup Script
echo ==========================================
echo.

:: Define Paths relative to this script
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%..\my_env"
set "BACKEND_DIR=%BASE_DIR%backend"
set "FRONTEND_DIR=%BASE_DIR%frontend"
set "REQ_FILE=%BASE_DIR%requirements.txt"

:: 1. Check for Python 3.12
echo [INFO] Checking Python 3.12...
set "PY_CMD="

:: Try 'py -3.12' launcher first
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py -3.12"
) else (
    :: Fallback to 'python' if it is version 3.12
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
        set "full_ver=%%v"
        if "!full_ver:~0,4!"=="3.12" (
            set "PY_CMD=python"
        )
    )
)

if "!PY_CMD!"=="" (
    echo [ERROR] Python 3.12 is required but not found.
    echo Please install Python 3.12 from python.org and try again.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('!PY_CMD! --version 2^>^&1') do set py_ver=%%v
echo [OK] Python %py_ver% found (using !PY_CMD!).

:: 2. Check for Node.js v24 (or higher)
echo [INFO] Checking Node.js version...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed.
    echo Please install Node.js v24 or later.
    pause
    exit /b 1
)

for /f "tokens=1" %%v in ('node -v 2^>^&1') do set node_ver=%%v
echo %node_ver% | findstr /r "^v2[4-9] ^v[3-9][0-9]" >nul
if %errorlevel% neq 0 (
    echo [WARNING] Node.js version is %node_ver%. Recommended version is v24 or later.
)
echo [OK] Node.js %node_ver% found.

:: 3. Create Python Virtual Environment
if not exist "%VENV_DIR%" (
    echo [INFO] Creating Python virtual environment at:
    echo        %VENV_DIR%
    !PY_CMD! -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [OK] Virtual environment 'my_env' already exists.
)

:: 4. Install Backend Dependencies
if not exist "%REQ_FILE%" (
    echo [ERROR] requirements.txt not found at %REQ_FILE%
    pause
    exit /b 1
)

echo [INFO] Installing Backend dependencies...
call "%VENV_DIR%\Scripts\activate"
python -m pip install --upgrade pip
pip install -r "%REQ_FILE%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)

:: 5. Setup Environment Variables (.env)
if exist "%BACKEND_DIR%\.env.example" (
    if not exist "%BACKEND_DIR%\.env" (
        echo [INFO] Creating .env file from .env.example...
        copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    ) else (
        echo [OK] backend/.env already exists.
    )
)

:: 6. Run Database Migrations
if exist "%BACKEND_DIR%\alembic.ini" (
    echo [INFO] Running database migrations...
    pushd "%BACKEND_DIR%"
    :: Ensure venv is active for alembic
    call "%VENV_DIR%\Scripts\activate"
    alembic upgrade head
    if %errorlevel% neq 0 (
        echo [WARNING] Database migration failed. This often happens if the database already exists.
        echo           If you already have tables, you might need to run: alembic stamp head
    )
    popd
)

:: 7. Install Frontend Dependencies
if exist "%FRONTEND_DIR%\package.json" (
    echo [INFO] Installing Frontend dependencies...
    pushd "%FRONTEND_DIR%"
    :: Use --legacy-peer-deps to resolve dependency conflicts
    call npm install --legacy-peer-deps
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies.
        popd
        pause
        exit /b 1
    )
    popd
) else (
    echo [WARNING] Frontend directory or package.json not found.
)

echo.
echo ==========================================
echo  Setup Complete! 
echo  Environment: %VENV_DIR%
echo  You can now run 'run_all_dev.bat'
echo ==========================================
pause
