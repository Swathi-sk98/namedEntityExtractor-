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
df = pd.read_csv("QA.csv")
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

matcher = NodeMatcher(graph)
rel_match=RelationshipMatcher(graph)
user = input("Enter the question:")

ent=[]
ent.append(get_entities(user))
for i in ent:
    s = i[0].lower()
    t = i[1].lower()

rel = get_relation(user).lower()
print(s)
print(t)
print(rel)

tx=graph.begin()
ques_match_user = matcher.match('question',name=user.lower()).first()
if ques_match_user is not None:
    m = graph.relationships.match((ques_match_user,None),'Answer is').first()
    #answer_to_user = graph.nodes(m)
    print(m.start_node['name'])
    print(m.end_node['name'])

else:
    s_node_match1 = matcher.match('source',name=s).first()
    s_node_match2 = matcher.match('target',name=s).first()

    if s_node_match1 is not None:
        final_s = s_node_match1
    elif s_node_match2 is not None:
        final_s = s_node_match2
    else:
        final_s = None

    t_node_match1 = matcher.match('target',name=t).first()
    t_node_match2 = matcher.match('source',name=t).first()

    if t_node_match1 is not None:
        final_t = t_node_match1
    elif t_node_match2 is not None:
        final_t = t_node_match2
    else:
        final_t = None

    m = graph.relationships.match((final_s,final_t),rel).first()
    
    if m is not None:
        ques_match = graph.relationships.match((final_t,None),'Answer is').first()
        print(ques_match.end_node['name'])   
    
