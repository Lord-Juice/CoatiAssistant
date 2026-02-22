@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist "venv\" (
  echo [ERROR] venv not found. Run setup.bat first.
  exit /b 1
)

if not exist "app\cli_chat.py" (
  echo [ERROR] app\cli_chat.py not found.
  exit /b 1
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Failed to activate venv.
  exit /b 1
)

python "app\cli_chat.py"
exit /b %errorlevel%
