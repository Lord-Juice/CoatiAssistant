@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist "requirements.txt" (
  echo [ERROR] requirements.txt not found in %cd%
  exit /b 1
)

if not exist "venv\" (
  echo [INFO] Creating venv in %cd%\venv ...
  py -3.12 -m venv venv
  if errorlevel 1 (
    echo [ERROR] "Failed to create venv. Is Python launcher (py) installed?"
    exit /b 1
  )
) else (
  echo [INFO] venv already exists.
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Failed to activate venv.
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] pip upgrade failed.
  exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install requirements.
  exit /b 1
)

echo [OK] Agent Core setup complete.
exit /b 0
