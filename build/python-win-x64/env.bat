@echo off

::SET PYTHON_VERSION=3.11.9
rem -- Specify the path to your .env file
set ENV_FILE=%~dp0../../.env

rem -- Check if the .env file exists
if not exist "%ENV_FILE%" (
    echo [%0]  .env file not found
    exit /b 1
)

rem -- Load variables from .env file
for /f "delims=" %%i in (%ENV_FILE%) do (
    set %%i
)

::echo [%0] Loaded PYTHON_VERSION=%PYTHON_VERSION%