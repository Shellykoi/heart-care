@echo off
chcp 65001 >nul
cd /d "%~dp0src\backend"
python sync_all_data_to_cloud.py
pause

