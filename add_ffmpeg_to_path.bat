@echo off
REM Run this batch file as Administrator to update the system PATH for FFmpeg
set SCRIPT_PATH=%~dp0add_ffmpeg_to_path.ps1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_PATH%"' -Verb RunAs"
