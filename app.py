import nltk
import os
from flask import Flask,request,jsonify,render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from celery import Celery
from nltk.tokenize import sent_tokenize,word_tokenize


app = Flask(__name__)

#mongoDB configuration
app.config["MONGO_DBNAME"]= "Entities"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Entities"


#Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

#Initialize extensions
mongo = PyMongo(app)

#initialize Celery
celery = Celery(app.name, broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

    
@celery.task(bind=True)
def extract_entity(self,input_text):
    """Background task to extract named entities."""
    self.input_text = input_text
    tokenized = nltk.sent_tokenize(input_text)
    for i in tokenized:
        words = nltk.word_tokenize(i)
        tagged = nltk.pos_tag(words)
        n = []

        named_ent = nltk.ne_chunk(tagged)

        for chunk in named_ent:
            if hasattr(chunk, 'label'):
                chunk = chunk[0]
            (name,tag) = chunk
            if tag == 'NN':
                n.append(name)

        dictionary = [{
            'text':input_text,
            'entities':n
            }]
             
        namedEntities = mongo.db.namedEntities
        dictionary_add = {'name':dictionary}
        namedEntities.insert(dictionary_add)
        
        return named_ent


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/process_content',methods = ["POST"])
def process_content():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        task = extract_entity.delay(rawtext)                           
                           
        return render_template("index.html", celery = task )
                                                                                     

if __name__ == '__main__':
    app.run(debug=True)
