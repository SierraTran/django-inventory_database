#!/bin/bash
# Install required packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Run the production server
gunicorn inventory_database.wsgi:application --bind 127.0.0.1:8000 --workers 3

# Open the browser (optional, depends on the environment)
xdg-open "http://127.0.0.1:8000/inventory_database"