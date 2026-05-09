@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Git Push Helper
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

:: 3. Ask for commit message
set /p msg="Enter commit message (Press Enter for 'Update'): "

if "!msg!"=="" (
    set "msg=Update"
)

:: 4. Execute git commands
echo.
echo [INFO] Adding all changes...
git add .

echo [INFO] Committing changes: "!msg!"
git commit -m "!msg!"

echo [INFO] Pushing !CURRENT_BRANCH! to origin...
git push origin !CURRENT_BRANCH!

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed. You might need to 'git pull' first.
) else (
    echo.
    echo ==========================================
    echo  Push Complete!
    echo ==========================================
)

pause
