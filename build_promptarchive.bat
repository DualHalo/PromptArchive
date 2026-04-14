@echo off
setlocal EnableDelayedExpansion

set "PROJECT_NAME=PromptArchive"
set "PROJECT_DIR=%~dp0"

echo ==========================================
echo Building %PROJECT_NAME% project structure...
echo ==========================================

if not exist "%PROJECT_DIR%templates" mkdir "%PROJECT_DIR%templates"
if not exist "%PROJECT_DIR%static" mkdir "%PROJECT_DIR%static"

if not exist "%PROJECT_DIR%venv" (
    echo Creating virtual environment...
    py -3 -m venv "%PROJECT_DIR%venv"
) else (
    echo Virtual environment already exists.
)

call "%PROJECT_DIR%venv\Scripts\activate.bat"

python -m pip install --upgrade pip
pip install -r "%PROJECT_DIR%requirements.txt"

python -c "from app import init_db; init_db(); print('Database initialized.')"

echo.
echo ==========================================
echo Build complete.
echo.
echo Next:
echo   1. Run run_promptarchive.bat
echo   2. Optionally run init_github_backup.bat
echo ==========================================
pause
