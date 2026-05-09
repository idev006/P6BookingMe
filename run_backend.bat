@echo off
TITLE P6BookingMe - Backend Dev Server
set CURRENT_DIR=%~dp0
cd /d "%CURRENT_DIR%backend"

echo Starting Backend in Dev Mode...
:: Check if virtual environment exists
if exist "%CURRENT_DIR%..\my_env\Scripts\activate" (
    echo Activating Virtual Environment from ..\my_env...
    call "%CURRENT_DIR%..\my_env\Scripts\activate"
) else if exist "%CURRENT_DIR%venv\Scripts\activate" (
    echo Activating Virtual Environment from workspace root...
    call "%CURRENT_DIR%venv\Scripts\activate"
)

:: Run uvicorn with hot-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
