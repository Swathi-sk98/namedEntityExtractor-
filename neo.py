import re
import pandas as pd
import bs4
import requests
import spacy
import os
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import networkx as nx
from neo4j.v1 import GraphDatabase,basic_auth
import matplotlib.pyplot as plt
from tqdm import tqdm
from py2neo.data import Node,Relationship,Walkable
from py2neo import Graph,NodeMatcher,RelationshipMatcher
graph=Graph("bolt://localhost:7687",user = "neo4j", password = "123456")

#graph.delete_all()


import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

pd.set_option('display.max_colwidth',200)
df = pd.read_csv("new Q&A.csv")
df.shape


def get_entities(sent):
  ## chunk 1
  ent1 = ""
  ent2 = ""

  prv_tok_dep = ""    # dependency tag of previous token in the sentence
  prv_tok_text = ""   # previous token in the sentence

  prefix = ""
  modifier = ""

  #############################################################
  
  for tok in nlp(sent): 
   
 
    ## chunk 2
    # if token is a punctuation mark then move on to the next token
    if tok.dep_ != "punct":
      # check: token is a compound word or not
      if tok.dep_ == "compound":
        prefix = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          prefix = prv_tok_text + " "+ tok.text
      
      # check: token is a modifier or not
      if tok.dep_.endswith("mod") == True:
        modifier = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          modifier = prv_tok_text + " "+ tok.text
      
      ## chunk 3
      if tok.dep_.find("subj") == True:
        ent1 = modifier +" "+ prefix + " "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""      

      ## chunk 4
      if tok.dep_.find("obj") == True:
        ent2 = modifier +" "+ prefix +" "+ tok.text
        
      ## chunk 5  
      # update variables
      prv_tok_dep = tok.dep_
      prv_tok_text = tok.text
  #############################################################

  return [ent1.strip(), ent2.strip()]

def get_relation(sent):

  doc = nlp(sent)

  # Matcher class object 
  matcher = Matcher(nlp.vocab)

  #define the pattern 
  pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

  matcher.add("matching_1", None, pattern) 

  matches = matcher(doc)
  k = len(matches) - 1

  span = doc[matches[k][1]:matches[k][2]] 

  return(span.text)
entity_pairs = []
relations = [get_relation(i) for i in tqdm(df['Question'])]


for i in tqdm(df[ "Question"]):
 entity_pairs.append(get_entities(i))
source = [i[0] for i in entity_pairs]
target = [i[1] for i in entity_pairs]
kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations, 'question':df['Question'], 'answer':df['Answer']})


matcher = NodeMatcher(graph)
rel_match=RelationshipMatcher(graph)

for i in range(len(kg_df)):
    tx = graph.begin()
    
    qs = matcher.match("source",name=source[i].lower()).first()
    qt = matcher.match("target",name=source[i].lower()).first()
    
    
    if qs is not None:
        a = qs
    elif qt is not None:
        a=qt
    else:
        a=Node("source",name=source[i].lower())
        tx.create(a)

    
    
    rt=matcher.match("target",name=target[i].lower()).first()
    rs=matcher.match("source",name=target[i].lower()).first()
    
    if rt is not None:
        b=rt
    elif rs is not None:
        b=rs
    else:
        b=Node("target",name=target[i].lower())
        tx.create(b)
    
    
    q = matcher.match("question",name=df['Question'][i].lower()).first()
    if q is None:
        ques = Node("question",name=df['Question'][i].lower())
        tx.create(ques)
    else:
        ques=q
 
    z = matcher.match("answer",name=df['Answer'][i]).first()
    if z is None:
        ans = Node("answer",name=df['Answer'][i])
        tx.create(ans) 
    else:
        ans=z  

    r = graph.relationships.match((a,b),relations[i].lower()).first()
    if r is None:
        if a == b:
            continue
        else:
            ab=Relationship(a,relations[i].lower(),b)
            tx.create(ab)
    else:
        ab = r

    ra = graph.relationships.match((ques,ans),'Answer is').first()
    
    if ra is None:
        if ques==ans:
            continue
        else:
            qa = Relationship(ques,'Answer is',ans)
            tx.create(qa)
    else:
        qa = ra

    w=ab+Relationship(b,'Answer is',ans)
    tx.create(w)
    
    tx.commit()
        


'''for i in range(len(kg_df)):
    for rel in graph.match(start_node=source[i]):
        print(rel.rel_type.properties[relations[i]],rel.end_node.properties[target[i]])
    a=Node("source",name=source[i])
    b=Node("target",name=target[i])
    ab=Relationship(a,relations[i],b)
    graph.create(ab)
    print(ab)
    
G=nx.from_pandas_edgelist(kg_df[kg_df['edge']=="is"], "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())


plt.figure(figsize=(12,12))
pos = nx.spring_layout(G, k = 0.5) # k regulates the distance between nodes
nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
plt.show()
'''
