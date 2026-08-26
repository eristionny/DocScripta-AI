@echo off
chcp 65001 >nul
cd /d "C:\Users\TONNY\Documents\robo-academico\DocScripta-AI"
echo.
echo =============================================
echo   Corrigir textareas desabilitadas
echo =============================================
echo.
"C:\Users\TONNY\AppData\Local\Programs\Python\Python311\python.exe" corrigir_textarea.py
pause
