Named Entity Extractor.

INSTALLING DEPENDENCIES


·       cd to the directory where requirements.txt is located

·       activate your virtualenv.

·       run:pip install -r requirements.txt in your shell.
  
·       Install mongoDB in your system.

·       Install redis which is compatible to your system.

·       Keep all the installed things ready.

  
  RUNNING THE CODE
  
  
· You need three processes running in order to run the application.

· Command prompt #1: REDIS: change directory to redis cotaining folder. Type 'src/redis-server'. Minimize.

· Command prompt #2:CELERY: Change directory to the virtual environment which contains the code. Type 'celery worker -A         app.celery --loglevel = info'. Minimize

· Command prompt #3:CODE: Change directory to the folder containing the code. Run it using 'python app.py'.Minimize.

· Copy the URL and paste it in browser to open html form.

· Type the INPUT .And click submit.

. To view the contents in the web page, change the URL to  /view_entities.


. To run the code in POSTman got to branch postman.
