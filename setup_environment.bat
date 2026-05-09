@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Environment Setup Script
echo ==========================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Python found.

:: 2. Check for Node.js
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Node.js found.

:: 3. Create Python Virtual Environment in the PARENT folder
if not exist "..\my_env" (
    echo [INFO] Creating Python virtual environment (..\my_env)...
    python -m venv "..\my_env"
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
