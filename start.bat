@echo off
setlocal
cd /d %~dp0

echo Ghost Talent launcher
echo --------------------

set PYTHON_BIN=
for %%P in (py python python3) do (
  where %%P >nul 2>nul
  if not errorlevel 1 (
    %%P -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 (
      set PYTHON_BIN=%%P
      goto :python_found
    )
  )
)

echo Python 3.10 or newer is required.
echo Install Python 3.10+ and run start.bat again.
pause
exit /b 1

:python_found
echo Using Python launcher: %PYTHON_BIN%

if not exist .venv (
  echo Creating local environment...
  %PYTHON_BIN% -m venv .venv
  if errorlevel 1 goto :fail
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto :fail

python -m pip install --upgrade "pip<26" "setuptools<76" >nul
if errorlevel 1 goto :fail
python -m pip install -e .
if errorlevel 1 goto :fail

echo Starting Ghost Talent at http://127.0.0.1:8765
start "" http://127.0.0.1:8765
python -m ghost_talent.app
exit /b %errorlevel%

:fail
echo.
echo Ghost Talent could not start. Review the error above.
pause
exit /b 1
