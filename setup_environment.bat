@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Environment Setup Script
echo ==========================================
echo.

:: 1. Check for Python 3.12
echo [INFO] Checking Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 is not installed or 'py' launcher is missing.
    echo Please install Python 3.12 and try again.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('py -3.12 --version 2^>^&1') do set py_ver=%%v
echo [OK] Python %py_ver% found.

:: 2. Check for Node.js v24
echo [INFO] Checking Node.js version...
for /f "tokens=1" %%v in ('node -v 2^>^&1') do set node_ver=%%v
echo %node_ver% | findstr /r "^v24" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Required Node.js v24.x, but found %node_ver%.
    echo Please install Node.js v24 and try again.
    pause
    exit /b 1
)
echo [OK] Node.js %node_ver% found.

:: 3. Create Python Virtual Environment in the PARENT folder
if not exist "..\my_env" (
    echo [INFO] Creating Python 3.12 virtual environment (..\my_env)...
    py -3.12 -m venv "..\my_env"
) else (
    echo [OK] Virtual environment 'my_env' already exists in parent folder.
)

:: 4. Install Backend Dependencies
echo [INFO] Installing Backend dependencies...
call "..\my_env\Scripts\activate"
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)
cd ..

:: 5. Setup Environment Variables (.env)
if not exist "backend\.env" (
    echo [INFO] Creating .env file from .env.example...
    copy backend\.env.example backend\.env
)

:: 6. Run Database Migrations
echo [INFO] Running database migrations...
cd backend
call "..\..\my_env\Scripts\activate"
alembic upgrade head
cd ..

:: 7. Install Frontend Dependencies
echo [INFO] Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    exit /b 1
)
cd ..

echo.
echo ==========================================
echo  Setup Complete! 
echo  You can now run 'run_all_dev.bat'
echo ==========================================
pause
