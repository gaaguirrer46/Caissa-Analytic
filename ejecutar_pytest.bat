@echo off
set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist "%PYTHON_PATH%" (
    "%PYTHON_PATH%" -m pytest tests/test_objetivos_smart.py -v
) else (
    python -m pytest tests/test_objetivos_smart.py -v
)
pause
