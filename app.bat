@echo off
:: Install required packages
pip install -r requirements.txt

:: Migrations for the web app
py manage.py makemigrations
py manage.py migrate

:: Run the server
start /b py manage.py runserver

:: Wait a moment to make sure the server is up and running
timeout /t 5 

:: Open a browser to the home page URL
start "" "http://127.0.0.1:8000/inventory_database"