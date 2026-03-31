@echo off
echo ==================================================
echo   Mehal Lab Inventory - Build Tool
echo ==================================================
echo.

cd /d "%~dp0"
echo Working directory: %cd%
echo.

set PYTHON=C:\Users\suyav\AppData\Local\Programs\Python\Python313\python.exe
if not exist "%PYTHON%" set PYTHON=C:\Users\suyav\AppData\Local\Programs\Python\Python311\python.exe
if not exist "%PYTHON%" (
    echo ERROR: Python not found. Install from https://www.python.org
    pause
    exit /b 1
)

echo Using: %PYTHON%
"%PYTHON%" --version
echo.

REM ---- Verify required files exist ----
echo Checking project files...
if not exist "launcher.py" (
    echo ERROR: launcher.py not found in %cd%
    pause
    exit /b 1
)
if not exist "frontend\index.html" (
    echo ERROR: frontend\index.html not found in %cd%
    pause
    exit /b 1
)
if not exist ".env" (
    echo ERROR: .env not found in %cd%
    pause
    exit /b 1
)
if not exist "app\main.py" (
    echo ERROR: app\main.py not found in %cd%
    pause
    exit /b 1
)
echo All project files found.
echo.

REM ---- Clean old build ----
if exist "venv" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo.

REM ---- Create venv ----
echo [1/4] Creating virtual environment...
"%PYTHON%" -m venv venv
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment creation failed.
    pause
    exit /b 1
)
echo Done.
echo.

REM ---- Install packages ----
echo [2/4] Installing packages (1-3 minutes)...
venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel --quiet
venv\Scripts\python.exe -m pip install fastapi==0.115.0 uvicorn==0.30.0 sqlalchemy==2.0.35 pydantic==2.9.0 pydantic-settings==2.5.0 python-multipart==0.0.9 python-dotenv==1.0.1 --quiet
venv\Scripts\python.exe -m pip install "python-jose[cryptography]==3.3.0" passlib==1.7.4 bcrypt==4.0.1 --quiet
venv\Scripts\python.exe -m pip install pyinstaller==6.11.1 --quiet

echo.
echo Verifying packages...
venv\Scripts\python.exe -c "import fastapi; import uvicorn; import sqlalchemy; import jose; import passlib; print('All packages OK')"
if errorlevel 1 (
    echo ERROR: Package verification failed.
    pause
    exit /b 1
)
echo.

REM ---- Build .exe ----
echo [3/4] Building .exe (2-5 minutes, please wait)...
venv\Scripts\python.exe -m PyInstaller mehal_lab.spec --noconfirm --clean
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. Check errors above.
    pause
    exit /b 1
)
echo.

REM ---- Copy supporting files next to .exe ----
echo [4/4] Copying frontend and config next to .exe...
if not exist "dist\MehalLabInventory\frontend" mkdir "dist\MehalLabInventory\frontend"
copy /Y "frontend\index.html" "dist\MehalLabInventory\frontend\" >nul
copy /Y ".env" "dist\MehalLabInventory\" >nul

echo.
echo ==================================================
echo   BUILD COMPLETE!
echo ==================================================
echo.
echo   Your app: %cd%\dist\MehalLabInventory\MehalLabInventory.exe
echo   Double-click to start. Browser opens automatically.
echo.
echo   To share: zip the entire dist\MehalLabInventory folder.
echo.
pause
