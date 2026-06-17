import re

# ==========================================
# 1. UPDATE server.py
# ==========================================
py = open('server.py', 'r', encoding='utf-8').read()

# Fix login vehicles
login_old = """resp["vehicles"] = user.get("vehicles", [])"""
login_new = """raw_vehicles = user.get("vehicles", [])
            resp["vehicles"] = [{"number": v} if isinstance(v, str) else v for v in raw_vehicles]"""
py = py.replace(login_old, login_new)

# Fix customer sales vehicles extraction
sales_old = """vehicles = [v.get("number", "") for v in user.get("vehicles", [])]"""
sales_new = """vehicles = [v.get("number", "") if isinstance(v, dict) else v for v in user.get("vehicles", [])]"""
py = py.replace(sales_old, sales_new)

open('server.py', 'w', encoding='utf-8').write(py)

# ==========================================
# 2. UPDATE app.js
# ==========================================
js = open('app.js', 'r', encoding='utf-8').read()

# Make sure displaying vehicles handles both strings and objects cleanly
veh_disp_old = """document.getElementById('cust-veh-disp').textContent = window.CUST_VEHICLES.map(v => v.number).join(', ') || 'None';"""
veh_disp_new = """document.getElementById('cust-veh-disp').textContent = window.CUST_VEHICLES.map(v => typeof v === 'object' ? (v.number || '') : v).join(', ') || 'None';"""
js = js.replace(veh_disp_old, veh_disp_new)

open('app.js', 'w', encoding='utf-8').write(js)

# ==========================================
# 3. UPDATE start.bat
# ==========================================
bat_content = """@echo off
echo ===================================================
echo     Starting PetroSync Smart Petrol Bunk System
echo ===================================================
echo.

echo Checking MongoDB Status...
tasklist /fi "imagename eq mongod.exe" | find ":" > nul
if errorlevel 1 (
    echo MongoDB is running.
) else (
    echo MongoDB is NOT running. Starting MongoDB automatically...
    start /min mongod --dbpath="C:\data\db"
    timeout /t 3 > nul
)

echo.
echo Checking Virtual Environment...
if not exist "venv" (
    echo Creating Virtual Environment...
    python -m venv venv
)
call venv\\Scripts\\activate.bat

echo.
echo Installing Requirements...
pip install -r requirements.txt

echo.
echo Starting Flask API Backend...
start http://localhost:8000/
python server.py

echo.
echo PetroSync stopped.
pause
"""
open('start.bat', 'w', encoding='utf-8').write(bat_content)

print("Patching V4 Complete.")
