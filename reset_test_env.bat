@echo off
echo Resetting Django Job Tracker Test Environment...
echo.

REM Set environment variable
set DJANGO_SETTINGS_MODULE=job_tracker.settings.test
echo Environment set to: %DJANGO_SETTINGS_MODULE%

REM Remove test database if it exists
if exist db_test.sqlite3 (
    echo Removing existing test database...
    del db_test.sqlite3
)

REM Run migrations
echo.
echo Running migrations...
python manage.py migrate

REM Create superuser
echo.
echo Creating superuser...
python manage.py create_superuser

REM Seed test data
echo.
echo Seeding test data...
python manage.py seed_test_data

echo.
echo ========================================
echo Test environment reset complete!
echo ========================================
echo.
echo Admin URL: http://127.0.0.1:8000/admin/
echo Username: Brieuc
echo Password: password
echo.
echo To start the server:
echo python manage.py runserver
echo.
pause
