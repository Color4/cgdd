@ECHO OFF

REM set PATH=C:\Users\HP\AppData\Local\Programs\Python\Python35;%PATH%

python manage.py runserver --noreload

REM  --noreload    : Disables the auto-reloader. This means any Python code changes you make while the server is running will not take effect if the particular Python modules have already been loaded into memory.
REM  --nothreading : Disables use of threading in the development server. The server is multithreaded by default.

