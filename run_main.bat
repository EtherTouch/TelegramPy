@echo off

cd /d "%~dp0"

set "PYTHONPATH=%PYTHONPATH%;%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

:restart
"%PYTHON_EXE%" .\telegrampy\main.py

echo.
echo App crashed. Restarting in 60 seconds...

REM Wait 60 seconds
timeout /t 60 /nobreak >nul

goto restart