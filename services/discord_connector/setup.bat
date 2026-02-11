@echo off
REM Create virtual environment for discord_connector
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv and install requirements
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Setup complete! Run start.bat to start the bot.
pause
