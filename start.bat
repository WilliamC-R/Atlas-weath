@echo off
echo ===============================
echo Iniciando Atlas Wealth...
echo ===============================
cd /d %~dp0
SET PYTHON=.venv\Scripts\python.exe
IF NOT EXIST %PYTHON% (
    echo Criando ambiente virtual...
    py -m venv .venv
)
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install -r requirements.txt
start http://127.0.0.1:8000
%PYTHON% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
