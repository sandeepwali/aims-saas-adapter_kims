@echo off
SETLOCAL

SET PYTHON_BUILD=%~dp0\python-win-x64\python-build.bat
SET SOLUM_BUILD=%~dp0\solum-scripts-package-win-x64\solum-build.bat

echo [%0] Building SOLUM Scripts Package for Windows x64

echo [%0] Building Python environment
CALL "%PYTHON_BUILD%"
echo [%0] Python environment built successfully

echo [%0] Building SOLUM Scripts Package
CALL "%SOLUM_BUILD%"
echo [%0] SOLUM Scripts Package built successfully

echo [%0] Done


