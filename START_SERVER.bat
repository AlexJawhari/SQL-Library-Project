@echo off
echo ========================================
echo Library Management System - Starting Server
echo ========================================
echo.

REM Kill any existing Python processes and processes on port 5000
echo Killing existing processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Also kill any processes using port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Navigate to backend directory
cd Milestone3\backend

REM Check if database exists
if not exist library.db (
    echo WARNING: Database file not found!
    echo Run 'python init_db.py' and 'python data_import.py' first.
    echo.
)

REM Start server
echo Starting Flask server on http://127.0.0.1:5000
echo Press CTRL+C to stop the server
echo ========================================
echo.

python app.py

