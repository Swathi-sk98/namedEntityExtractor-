Named Entity Extractor.

INSTALLING DEPENDENCIES


·       cd to the directory where requirements.txt is located

·       activate your virtualenv.

·       run:pip install -r requirements.txt in your shell.
  
·       Install mongoDB in your system.

·       Install redis which is compatible to your system. Run redis as a service. Type 'sudo systemctl start redis'

·       Keep all the installed things ready.

  
  RUNNING THE CODE

· Command prompt #1:CELERY: Change directory to the virtual environment which contains the code. Type 'celery worker -A         app.celery --loglevel = info'. Minimize

· Command prompt #2:CODE: Change directory to the folder containing the code. Run it using 'python app.py'.Minimize.

  POSTMAN COLLECTION
  
. POSTman collections link: https://www.getpostman.com/collections/454216de7f3420bf648a

  METHODS 

.  /test : Take the JSON input and give the extracted entities as JSON output.

.  /extract : Take the input as form data, start the background task and give the extracted entities in JSON format.

.  /view : Give a listing of previous extractions in JSON format.
