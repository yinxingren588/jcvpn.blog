@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\prepare_release.ps1"
pause
