@echo off
chcp 65001 >nul
python -c "import pypdf" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r "%~dp0requirements.txt"
)
python "%~dp0src\compress.py"
pause
