@echo off
:: Install required packages
pip install -r requirements.txt

:: Collect static files
py manage.py collectstatic --noinput

:: Apply migrations for the web app
py manage.py makemigrations
py manage.py migrate

:: Run the server
start /b waitress-serve --host=127.0.0.1 --port=8000 inventory_database.wsgi:application

:: Wait a moment to make sure the server is up and running
timeout /t 5 /nobreak

:: Open a browser to the home page URL
start "" "http://127.0.0.1:8000/inventory_database"