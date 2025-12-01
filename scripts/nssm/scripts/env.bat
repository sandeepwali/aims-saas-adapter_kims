@echo off

REM CALL "%~dp0..\..\env.bat"

SET NSSM_EXEC=%~dp0..\win64\nssm.exe
SET APP_DIR=%~dp0..\..\..\
SET APP_BAT=%~dp0..\..\..\app.bat
SET SERVICE_NAME=aims-saas-adapter-kims