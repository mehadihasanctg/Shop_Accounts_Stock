@echo off
cd /d "%~dp0"
if exist instance\shop_accounts.db del /q instance\shop_accounts.db
echo Database reset complete. Run run.bat now.
pause
