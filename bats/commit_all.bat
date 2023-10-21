@echo off
setlocal enabledelayedexpansion

:: Change the current directory to the directory where commit_all.bat resides
::cd /d %~dp0

:: Recursively search for all autocommit.bat files and execute them
for /r %%i in (autocommit.bat) do (
    echo Executing: %%i
    call "%%i"
)

echo All autocommit.bat scripts executed!
pause
