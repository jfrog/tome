@echo off
REM tome_description: Script to perform a traceroute to an IP address or URL. Arguments: <IP or URL>.

IF "%~1"=="" (
    echo Usage: %0 ^<IP or URL^>
    exit /b 1
)

tracert %1
