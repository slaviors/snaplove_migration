@echo off
echo ============================================================
echo Snaplove MongoDB to MySQL Migration Tool
echo ============================================================
echo.

echo [0/4] Checking configuration file...
if not exist "config.py" (
    if exist "config.example.py" (
        echo WARNING: config.py not found. Creating from template...
        copy config.example.py config.py >nul
        echo.
        echo Please edit config.py and update MySQL credentials before continuing!
        echo.
        pause
        exit /b 1
    ) else (
        echo ERROR: config.example.py not found
        pause
        exit /b 1
    )
)
echo Config file found.
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/4] Running connection test...
python test_connection.py
if errorlevel 1 (
    echo.
    echo Please fix the issues above before running migration.
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Ready to migrate!
echo ============================================================
echo.
set /p confirm="Do you want to start migration now? (y/N): "
if /i "%confirm%"=="y" (
    echo.
    echo Starting migration...
    echo.
    python converter.py
    echo.
    echo ============================================================
    echo Migration process completed!
    echo ============================================================
) else (
    echo.
    echo Migration cancelled. Run 'python converter.py' when ready.
)
echo.
pause
