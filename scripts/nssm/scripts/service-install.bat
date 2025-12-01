@echo off
SETLOCAL

CALL "%~dp0env.bat"

set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~dp0"" && ""%~0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

echo Installing %APP_BAT% as a service

"%NSSM_EXEC%" install "%SERVICE_NAME%" "%APP_BAT%"

"%NSSM_EXEC%" set "%SERVICE_NAME%" AppDirectory %APP_DIR%
"%NSSM_EXEC%" set "%SERVICE_NAME%" DisplayName "%SERVICE_NAME%"
"%NSSM_EXEC%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START
"%NSSM_EXEC%" set "%SERVICE_NAME%" ObjectName LocalSystem
"%NSSM_EXEC%" set "%SERVICE_NAME%" Type SERVICE_WIN32_OWN_PROCESS
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppPriority NORMAL_PRIORITY_CLASS
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppNoConsole 0
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppAffinity All
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppStopMethodSkip 0
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppStopMethodConsole 1500
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppStopMethodWindow 1500
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppStopMethodThreads 1500
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppThrottle 1500
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppExit Default Restart
"%NSSM_EXEC%" set "%SERVICE_NAME%" AppRestartDelay 1500


