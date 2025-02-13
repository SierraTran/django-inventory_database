start cmd /k "pip install -r requirements.txt && python manage.py migrate && python manage.py runserver"
@ECHO OFF
ECHO Hello! The server for the Inventory Database application has been started up for you in another command window.
ECHO You can close this window when you're ready.
ECHO To stop the server for the app, simply close the other window.
ECHO It'll say "C:\Windows\system32\cmd.exe - python manage.py runserver" at the top.
ECHO You can always spin it back up by clicking the .bat file again.
PAUSE