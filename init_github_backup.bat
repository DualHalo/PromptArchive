@echo off
setlocal EnableDelayedExpansion

set "PROJECT_DIR=%~dp0"
set "REPO_NAME=PromptArchive"
set "GITHUB_USER=DualHalo"
set "REMOTE_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git"

cd /d "%PROJECT_DIR%"

where git >nul 2>&1
if errorlevel 1 (
    echo Git is not installed or not on PATH.
    pause
    exit /b 1
)

if not exist ".git" (
    echo Initializing local git repository...
    git init
)

git add .
git commit -m "Initial PromptArchive v1 commit" 2>nul
if errorlevel 1 (
    echo No new changes to commit, or commit already exists.
)

where gh >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI not found.
    echo.
    echo Local git repo is ready.
    echo Create the repo on GitHub, then run:
    echo git remote add origin %REMOTE_URL%
    echo git branch -M main
    echo git push -u origin main
    echo.
    pause
    exit /b 0
)

echo GitHub CLI found. Attempting repo creation...
gh repo create "%GITHUB_USER%/%REPO_NAME%" --public --source="%PROJECT_DIR%" --remote=origin --push
if errorlevel 1 (
    echo.
    echo GitHub repo creation did not complete automatically.
    echo You may already have a repo, or gh may need authentication.
    echo.
    echo If needed, run:
    echo gh auth login
    echo git remote add origin %REMOTE_URL%
    echo git branch -M main
    echo git push -u origin main
    echo.
    pause
    exit /b 0
)

echo.
echo GitHub backup complete.
pause
