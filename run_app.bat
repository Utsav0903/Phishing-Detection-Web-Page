@echo off
REM Adjust path if your project folder is different
SET PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Start server in a new window
start "PhishServer" cmd /k "call venv\Scripts\activate.bat && python app.py"

REM Wait a second then open browser to the app
timeout /t 2 /nobreak > nul
start "" "http://localhost:5000/"

exit /b 0
