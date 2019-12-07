import spacy
import os
from flask import Flask,request,jsonify,render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from celery import Celery
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)

#mongoDB configuration
app.config["MONGO_DBNAME"]= "Entities"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Entities"

#Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['RESULT_BACKEND'] = 'redis://localhost:6379'

#Initialize extensions
mongo = PyMongo(app)

#initialize Celery
celery = Celery(app.name, broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def extract_entity(self,input_text,flag):
    """Background task to extract named entities."""
    self.input_text = input_text
    self.flag = flag
    if flag == False:
        doc = nlp(input_text) #extracts entities
        ent = []

        for x in doc.ents:
            ent.append(x.text)
        
        dictionary = [{
            'text':input_text,
            'entities':ent
            }]
             
        namedEntities = mongo.db.namedEntities
        
        #updates in mongoDB
        namedEntities.update(
            {'text':input_text},
            dictionary,
            True
            )
             
        flag = True
        
    return doc


@app.route('/') #to check whether the application is running correctly on port
def index():
    return render_template("index.html")

@app.route('/store_content',methods = ["POST"])
def store_content():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        processed = False
        task = extract_entity.delay(rawtext,processed)   

               
        return render_template("index.html",celery = task)

@app.route('/view_entities', methods = ['GET'])  #viewing all contents of namedEntities
def get_entities():
    namedEntities = mongo.db.namedEntities
    Lists = []
    List = namedEntities.find()
    for j in List:
        j.pop('_id')
        Lists.append(j)
    return jsonify(Lists)

                                                                                  
if __name__ == '__main__':
    app.run(debug=True)