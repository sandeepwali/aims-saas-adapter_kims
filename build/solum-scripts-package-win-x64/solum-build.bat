@echo off
SETLOCAL

REM echo [%0] Loading environment variables
REM CALL "%~dp0env.bat"

echo [%0] Building SOLUM Scripts Package environment
PowerShell.exe -ExecutionPolicy Unrestricted -File "%~dp0\solum-build.ps1"
