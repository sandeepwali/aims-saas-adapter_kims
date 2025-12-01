@echo off
SETLOCAL

echo [%0] Loading environment variables
REM CALL "%~dp0env.bat"

rem -- Specify the path to your .env file
set ENV_FILE=%~dp0.env

rem -- Check if the .env file exists
echo [%0] Checking if %ENV_FILE% exists
if not exist "%ENV_FILE%" (
    echo [%0]  .env file not found
    exit /b 1
)

echo [%0] Loading environment variables from %ENV_FILE%
rem -- Load variables from .env file
for /f "usebackq tokens=* delims=" %%i in ("%ENV_FILE%") do (
    rem -- Trim leading and trailing spaces
    set "line=%%i"
    call :trim line

    rem -- Skip empty lines
    if not "!line!"=="" (
        rem -- Skip lines starting with #
        if not "!line:~0,1!"=="#" (
            rem -- Set the variable
            set %%i
        )
    )
)

echo [%0] Environment variables loaded
echo [%0] VERSION=%VERSION%
echo [%0] PYTHON_VERSION=%PYTHON_VERSION%


SET BIN_DIR=%~dp0bin
SET PYTHON_DIR=%BIN_DIR%\python-%PYTHON_VERSION%
SET PATH=%PATH%;%PYTHON_DIR%;%PYTHON_DIR%\Scripts
SET PYTHON_EXEC=%PYTHON_DIR%\python.exe

SET INCLUDE=%PYTHON_DIR%\Include;%INCLUDE%
set LIB=%PYTHON_DIR%\libs;%LIB%

echo [%0] Executing %PYTHON_EXEC% app.py
"%PYTHON_EXEC%" app.py


:trim
    setlocal enabledelayedexpansion
    set "string=!line!"
    for /f "tokens=* delims=" %%A in ("!string!") do (
        endlocal
        set "line=%%A"
    )
    exit /b