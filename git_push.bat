@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Git Push Helper
echo ==========================================
echo.

:: 1. Ask for commit message
set /p msg="Enter commit message: "

if "!msg!"=="" (
    echo [ERROR] Commit message cannot be empty.
    pause
    exit /b 1
)

:: 2. Execute git commands
echo.
echo [INFO] Adding all changes...
git add .

echo [INFO] Committing changes...
git commit -m "!msg!"

echo [INFO] Pushing to main...
git push origin main

echo.
echo ==========================================
echo  Push Complete!
echo ==========================================
pause
