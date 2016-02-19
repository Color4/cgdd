rem if db exists try to delete it. Can't just use '|| exit' as 'del' returns errorlevel of 0 even if can't delete the file, so just test again if still exists
if exist db.sqlite3 del db.sqlite3
if exist db.sqlite3 exit /b 1

del /S /Q gendep\migrations
python manage.py migrate || exit /b 2
python manage.py makemigrations gendep || exit /b 3
python manage.py sqlmigrate gendep 0001 || exit /b 4
python manage.py migrate || exit /b 5
python .\load_data.py || exit /b 6
