@echo off
echo Auto-Sync Started. Press Ctrl+C to stop.
:loop
git add .
git commit -m "Auto-backup: %date% %time%"
git push
echo Waiting 1 minute before next sync...
timeout /t 1 /nobreak
goto loop
