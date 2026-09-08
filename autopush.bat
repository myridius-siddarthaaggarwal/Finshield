@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXE=.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" set PYTHON_EXE=python

if "%~1"=="" (
    "%PYTHON_EXE%" agents\git_agent\git_agent.py autopush
) else (
    "%PYTHON_EXE%" agents\git_agent\git_agent.py autopush -m "%~1"
)
