@echo off
chcp 65001 >nul
echo PDF Kompressor - LLM Optimierung
echo ==================================
python "%~dp0scripts\compress_pdfs.py"
echo.
pause
