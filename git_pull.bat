@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Git Pull Helper
echo ==========================================
echo.

:: 1. Check if remote 'origin' exists
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Remote 'origin' not found. Adding default remote...
    git remote add origin https://github.com/idev006/P6BookingMe.git
)

:: 2. Get current branch name
for /f "tokens=*" %%b in ('git rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%b"
echo [INFO] Current branch: !CURRENT_BRANCH!

:: 3. Execute git pull
echo [INFO] Pulling latest changes from origin !CURRENT_BRANCH!...
git pull origin !CURRENT_BRANCH!

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Pull failed. Please check your internet connection or conflict.
) else (
    echo.
    echo ==========================================
    echo  Pull Complete!
    echo ==========================================
)

pause
