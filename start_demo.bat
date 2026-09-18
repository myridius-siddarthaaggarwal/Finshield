@echo off
setlocal
cd /d %~dp0
set PYTHON_EXE=.venv\Scripts\python.exe
if not exist %PYTHON_EXE% set PYTHON_EXE=py
%PYTHON_EXE% scripts\run_live_demo.py %*
pause
