@echo off
REM Start the discord_connector bot
if not exist venv (
    echo Error: Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python app\bot.py
pause
