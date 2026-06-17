@echo off
title PetroSync System Runner
echo ===================================================
echo     Starting PetroSync Smart Petrol Bunk System
echo ===================================================
echo.

echo [1/4] Checking MongoDB Status...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo MongoDB is already running.
) else (
    echo MongoDB is NOT running. Starting MongoDB automatically...
    if not exist "C:\data\db" mkdir "C:\data\db"
    start /min mongod --dbpath="C:\data\db"
    timeout /t 3 > nul
)

echo.
echo [2/4] Checking Virtual Environment...
if not exist "venv" (
    echo Creating Virtual Environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing Requirements...
pip install -r requirements.txt -q

echo.
echo [4/4] Starting PetroSync Server...
echo The application will open in your default browser shortly.
echo PLEASE DO NOT CLOSE THIS WINDOW.
echo.

:: Create a temporary script to open the browser after a short delay
echo WScript.Sleep 2500 > temp_launch.vbs
echo CreateObject("WScript.Shell").Run "http://localhost:8000/" >> temp_launch.vbs
start wscript temp_launch.vbs
timeout /t 1 > nul
del temp_launch.vbs

:: Start the Flask server
python server.py

pause
