@echo off
SETLOCAL

echo [%0] Loading environment variables
CALL "%~dp0env.bat"

echo [%0] Installing Python environment
SET BIN_DIR=%~dp0..\..\bin
SET PYTHON_VERSION_DIR_NAME=python-%PYTHON_VERSION%
SET PYENV_VERSION_DIR=%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%
SET PYTHON_EXEC=%~dp0python.bat
SET PYTHON_REQUIREMENTS=%~dp0..\..\requirements.txt

echo [%0] Install Python using Pyenv if it isn't already installed
CALL pyenv install %PYTHON_VERSION%

echo [%0] Remove the bin directory
IF EXIST "%BIN_DIR%" (
    rmdir /s /q "%BIN_DIR%"
)

echo [%0] Check if the target directory exists and create it if it doesn't

IF NOT EXIST "%BIN_DIR%" (
    mkdir "%BIN_DIR%"
)

IF NOT EXIST "%BIN_DIR%\%PYTHON_VERSION_DIR_NAME%" (
    mkdir "%BIN_DIR%\%PYTHON_VERSION_DIR_NAME%"
)

echo [%0] Copy the Python environment to the target directory
xcopy "%PYENV_VERSION_DIR%" "%BIN_DIR%\%PYTHON_VERSION_DIR_NAME%" /E /I /Y

echo [%0] Python environment copied to %BIN_DIR%\%PYTHON_VERSION_DIR_NAME%

echo [%0] Installing python requirements
CALL "%PYTHON_EXEC%" -m pip install --upgrade setuptools
CALL "%PYTHON_EXEC%" -m pip install --upgrade wheel
CALL "%PYTHON_EXEC%" -m pip install --upgrade -r "%PYTHON_REQUIREMENTS%"

echo [%0] Python environment installed successfully