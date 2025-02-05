@echo off
REM tome_description: Script to ping an IP address or URL. Arguments: <IP or URL>.

IF "%~1"=="" (
    echo Usage: %0 ^<IP or URL^>
    exit /b 1
)

ping -n 4 %1
