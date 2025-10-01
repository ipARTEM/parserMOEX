@echo off
setlocal
REM ===== Запуск локального сервера на порту 8089 =====
cd /d %~dp0
python -m uvicorn app.main:app --host 0.0.0.0 --port 8089 --reload