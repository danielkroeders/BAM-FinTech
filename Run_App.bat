@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

echo.
echo B2B Loan Fraud Intelligence
echo ---------------------------

if not exist "Home.py" (
    echo Home.py was not found. Please run this file from the project folder.
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo requirements.txt was not found. Please run this file from the project folder.
    echo.
    pause
    exit /b 1
)

if not exist "%VENV_PY%" (
    echo Creating local Python environment in .venv...
    call :create_venv
    if errorlevel 1 goto python_error
)

echo.
echo Installing or updating dependencies...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto pip_error

"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto pip_error

echo.
echo Starting Streamlit app...
echo A browser window should open automatically.
echo If it does not, open http://localhost:8501
echo.
"%VENV_PY%" -m streamlit run Home.py --server.headless=false --browser.gatherUsageStats=false
goto end

:create_venv
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv .venv
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)

where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 (
        python -m venv .venv
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)

exit /b 1

:python_error
echo.
echo Python 3.10 or newer was not found.
echo Install Python from https://www.python.org/downloads/
echo During installation, select "Add python.exe to PATH", then open Run_App.bat again.
echo.
pause
exit /b 1

:pip_error
echo.
echo Dependency installation failed.
echo Check your internet connection, then open Run_App.bat again.
echo.
pause
exit /b 1

:end
echo.
echo Streamlit stopped. You can close this window.
echo.
pause
