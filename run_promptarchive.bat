@echo off
setlocal

set "PROJECT_DIR=%~dp0"

if not exist "%PROJECT_DIR%venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Run build_promptarchive.bat first.
    pause
    exit /b 1
)

call "%PROJECT_DIR%venv\Scripts\activate.bat"

echo Starting PromptArchive...
python "%PROJECT_DIR%app.py"

pause
