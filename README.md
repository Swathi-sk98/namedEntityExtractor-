Named Entity Extractor.

INSTALLING DEPENDENCIES
·       Using pip command install spacy and all the other dependencies.
·       To install Flask , create virtual environment using virtualenv command.
·       And then in the virtual environment, activate Scripts using <env>/Scripts/activate. Inside virtual environment using         pip ,install flask. And then copy the file containing the code inside <env>.
·       Copy the html file inside the templates folder.
·       Install mongoDB in your system.
·       And then install celery using pip command
·       Install redis which is compatible to your system.
·       Keep all the installed things ready.
  
  RUNNING THE CODE
· You need four processes running in order to run the application.
· Command prompt #1: REDIS: change directory to redis cotaining folder. Type 'src/redis-server'. Minimize.
. Command prompt #2: REDIS: change directory to redis containing folder. Type 'src/redis-cli'. Minimize.
· Command prompt #3:CELERY: Change directory to the virtual environment which contains the code. Type 'celery worker -A         app.celery --loglevel = info'. Minimize
· Command prompt #4:CODE: Change directory to the folder containing the code. Run it using 'python app.py'.Minimize.
· Copy the URL and paste it in browser to open html form.
· Type the INPUT .And click submit.
· Command prompt #5: MONGODB: Check for the output (stored entities) in mongodb.
