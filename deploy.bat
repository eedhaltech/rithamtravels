@echo off
echo Installing deployment requirements...
pip install -r deploy_requirements.txt

echo.
echo Ritham Tours & Travels - File Upload Script
echo ==========================================
echo.

set /p HOST="Enter server hostname or IP: "
set /p USERNAME="Enter SSH username: "
set /p REMOTE_PATH="Enter remote path (default: /var/www/ritham_tours): "

if "%REMOTE_PATH%"=="" set REMOTE_PATH=/var/www/ritham_tours

echo.
echo Uploading files to %HOST%...
python deploy_files.py --host %HOST% --username %USERNAME% --remote-path %REMOTE_PATH%

pause