import spacy
import os
from flask import Flask,request,jsonify,render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from celery import Celery, current_app
from spacy import displacy
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)

#mongoDB configuration
app.config["MONGO_DBNAME"]= "Entities"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Entities"

#Initialize extensions
mongo = PyMongo(app)

#initialize Celery
def make_celery(app):
    celery = Celery(app.name, backend=app.config['RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return self.run(*args,**kwargs)
    celery.Task = ContextTask
    return celery

#Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['RESULT_BACKEND'] = 'redis://localhost:6379'
celery = make_celery(app)

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
    e=[]
       
    for x in doc.ents:
        print(x.text)
        e.append( x.text)
    return e


@app.route('/test',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        value = request.json['key']
        doc = nlp(value)
        ent = []
        for x in doc.ents:
            ent.append(x.text)
        return jsonify({"key":ent})


@app.route('/extract',methods=['POST'])
def extract():
    rawtext = request.form['rawtext']
    processed = False
    task = extract_entity.delay(rawtext,processed)
    print(task)
    r = task.wait()
        
    return jsonify({'key':r})


@app.route('/view',methods=['GET'])
def view():
    namedEntities = mongo.db.namedEntities
    Lists = []
    List = namedEntities.find()
    for j in List:
        j.pop('_id')
        Lists.append(j)
    return jsonify({'key':Lists})
    

    


@app.route('/store_content',methods = ["POST"])
def store_content():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        processed = False
        task = extract_entity.delay(rawtext,processed)
        print(task)
        r = task.wait()
        
        return render_template("index.html",results=r)

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
