@echo off
set BASE=%~dp0
set PYTHONPATH=
cd F:\Soft\Portable Python 2.7.3.1\App
F:
REM "%CD%\Scripts\pip" --proxy=http://rain.ifmo.ru:3128/ install protobuf
python.exe %BASE%\sessions-server.py