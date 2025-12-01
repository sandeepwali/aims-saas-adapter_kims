@echo off
SETLOCAL

echo [%0] Loading environment variables
CALL "%~dp0env.bat"

SET BIN_DIR=%~dp0..\..\bin
SET PYTHON_DIR=%BIN_DIR%\python-%PYTHON_VERSION%
SET PATH=%PATH%;%PYTHON_DIR%;%PYTHON_DIR%\Scripts
SET PYTHON_EXEC=%PYTHON_DIR%\python.exe

SET INCLUDE=%PYTHON_DIR%\Include;%INCLUDE%
set LIB=%PYTHON_DIR%\libs;%LIB%

::echo [%0] Executing %PYTHON_EXEC% %*
"%PYTHON_EXEC%" %*