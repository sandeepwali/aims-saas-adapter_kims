@echo off
SETLOCAL

SET BIN_DIR=%~dp0..\..\bin
SET LOGS_DIR=%~dp0..\..\logs
echo [%0] ----------------------------------------------------------------------------------------------------------------
echo [%0]                                               !!! WARNING !!!
echo [%0] ----------------------------------------------------------------------------------------------------------------
echo [%0] Purpose: This script is used to clean up the Python environment for development purposes.
echo [%0] Description: This script will remove the bin directory, the Superset database, and the log files in the logs directory.
echo [%0] ----------------------------------------------------------------------------------------------------------------
echo [%0] BIN_DIR: %BIN_DIR%
echo [%0] LOGS_DIR: %LOGS_DIR% 
echo [%0] ----------------------------------------------------------------------------------------------------------------
echo [%0] Close this windows if you do not want to clean up the Superset environment.
pause
echo [%0] Press any key again to continue
pause

echo [%0] Remove the bin directory
IF EXIST "%BIN_DIR%" (
    rmdir /s /q "%BIN_DIR%"
)

echo [%0] Remove the log files in the logs directory
IF EXIST "%LOGS_DIR%" (
    del /q "%LOGS_DIR%\*.log"
)

