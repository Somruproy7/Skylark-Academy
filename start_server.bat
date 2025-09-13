@echo off
echo =================================
echo   Skylark Academy Server Setup
echo =================================

echo Setting environment variables...
set AUTO_POPULATE_DB=true
set DB_NAME=skylark_academy
set DB_USER=root
set DB_PASSWORD=somrup7
set DB_HOST=localhost
set DB_PORT=3306

echo Changing to source directory...
cd /d "%~dp0\src"

echo Installing/upgrading required packages...
pip install mysqlclient==2.2.4

echo Starting Django development server...
echo Database will be created automatically if needed!
echo Migrations will run automatically!
echo Sample data will be populated automatically!
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Admin panel at: http://127.0.0.1:8000/admin/
echo.

python manage.py runserver

pause