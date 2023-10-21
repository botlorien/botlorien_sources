@echo off
setlocal enabledelayedexpansion

:: Change the current directory to the directory where commit_all.bat resides
::cd /d %~dp0

:: Recursively search for all autocommit.bat files and execute them
:: Search only for autocommit.bat files in the immediate child folders and execute them
for /d %%d in (*) do (
    if exist "%%d\autocommit.bat" (
        echo Executing: %%d\autocommit.bat
        call "%%d\autocommit.bat"
    )
)

echo All autocommit.bat scripts executed!
pause
