@echo off
cd /d "%~dp0"
echo [%date% %time%] bat ishga tushdi >> logs\scheduler.log
".venv\Scripts\python.exe" src\pipeline.py >> logs\scheduler.log 2>&1
set RC=%ERRORLEVEL%
echo [%date% %time%] bat tugadi, exit code %RC% >> logs\scheduler.log
exit /b %RC%