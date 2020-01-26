import spacy
from spacy.vocab import Vocab
import os
from flask import Flask,request,jsonify,render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from celery import Celery, current_app
from celery.bin import worker
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

#to add new entities.
custom_entities = ['Bootstrap','Oracle','Python','MySQL','Django']
p = nlp.get_pipe('ner')
for ent in custom_entities:
    if 'extra_labels' in p.cfg and ent in p.cfg['extra_labels']:
        pass
    else:
        p.add_label(ent)

p.cfg['extra_labels'] = custom_entities

#vocab = Vocab(strings=['bootstrap','oracle','python','mysql','django'])
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
        doc = nlp(input_text)
        ent = []

        for x in doc.ents:
            ent.append(x.text)
        
        dictionary = [{
            'text':input_text,
            'entities':ent
            }]
             
        namedEntities = mongo.db.namedEntities
        dictionary_add = {'name':dictionary}
        if namedEntities.find({'name':dictionary}).count()==0:
            namedEntities.insert(dictionary_add)
        
        flag = True
       
    for x in doc.ents:
        print(x.text)
        return x.text


@app.route('/')
def index():
    return render_template("index.html")



@app.route('/store_content',methods = ["POST"])
def store_content():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        processed = False
        task = extract_entity.delay(rawtext,processed)
        print(task)   

               
        return render_template("index.html",celery = task)

@app.route('/view_entities', methods = ['GET'])
def get_entities():
    namedEntities = mongo.db.namedEntities
    Lists = []
    List = namedEntities.find()
    for j in List:
        j.pop('_id')
        Lists.append(j)
    return render_template("listing.html",results = Lists)

                                                                                  
if __name__ == '__main__':
    app.run(debug=True)
