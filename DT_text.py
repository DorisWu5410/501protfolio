#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 03:05:07 2021

@author: jiahuiwu
"""

import pandas as pd

news_df = pd.read_csv('/Users/jiahuiwu/Desktop/501/discus3reply/GGnews.csv')

from sklearn.feature_extraction.text import TfidfVectorizer as tf

# cv = CountVectorizer(min_df=0, stop_words="english", max_features=200)
cv = tf(min_df=0, stop_words="english", max_features=200)


#select key words
all_doc = []
for i in range(0,len(news_df['Article'])):
    # if type(news_df['Article'][i]) is str:
    all_doc.append(str(news_df['Article'][i]))    
    
   
matrix = cv.fit_transform(all_doc).toarray()
 
word = cv.get_feature_names()

tf_dataframe = pd.DataFrame(columns=word,data=matrix)

tf_dataframe.to_csv('reply.csv')


#cluster    
from sklearn.cluster import KMeans    
def clust_kmean(k,data):
    kmeans = KMeans(n_clusters=k, max_iter=300, n_init=10, random_state=0)
    kmeans.fit(data)
    data['lable'] = kmeans.labels_
    return(data)


data1_2 = clust_kmean(3,tf_dataframe)



from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import random

random.seed(10)
idx1 = random.sample(range(1,len(data1_2)),int(len(data1_2)//1.2)) 

random.seed(20)
idx2 = random.sample(range(1,len(data1_2)),int(len(data1_2)//1.2)) 

random.seed(30)
idx3 = random.sample(range(1,len(data1_2)),int(len(data1_2)//1.2)) 
    
random.seed(40)
idx4 = random.sample(range(1,len(data1_2)),int(len(data1_2)//1.2)) 

def fit_tree(idx):
    alpha = 0.00029
    newtree = DecisionTreeClassifier(ccp_alpha = alpha)
    newtree.fit(data1_2.iloc[:,:-1].iloc[idx], data1_2['lable'].iloc[idx])
    return(newtree)



import pydotplus
import graphviz
from IPython.display import Image  
import pydotplus
from six import StringIO
import os

tree1 = fit_tree(idx1)
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
dot_data = StringIO()    
tree.export_graphviz(tree1, out_file= dot_data, 
                          feature_names= data1_2.columns[:-1],
                          class_names  = ['0','1','2'],
                          filled=True,rounded=True,
                          special_characters=True,
                      label='all',impurity=True,proportion=True,
                      
                    )  
graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
Image(graph.create_png())

predict1 = tree1.predict(data1_2.iloc[:,:-1].iloc[[s for s in range(len(data1_2)) if s not in idx1]])
ytrue = pd.Series(data1_2['lable'].iloc[[s for s in range(len(data1_2)) if s not in idx1]])
pd.crosstab(ytrue, predict1, rownames=['Actual'], colnames=['Predicted'], margins = True)



tree2 = fit_tree(idx2)
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
dot_data = StringIO()    
tree.export_graphviz(tree2, out_file= dot_data, 
                          feature_names= data1_2.columns[:-1],
                          class_names  = ['0','1','2'],
                          filled=True,rounded=True,
                          special_characters=True,
                      label='all',impurity=True,proportion=True,
                    )  
graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
Image(graph.create_png())

predict2 = tree2.predict(data1_2.iloc[:,:-1].iloc[[s for s in range(len(data1_2)) if s not in idx2]])
ytrue2 = pd.Series(data1_2['lable'].iloc[[s for s in range(len(data1_2)) if s not in idx2]])
pd.crosstab(ytrue2, predict2, rownames=['Actual'], colnames=['Predicted'], margins = True)



tree3 = fit_tree(idx1)
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
dot_data = StringIO()    
tree.export_graphviz(tree3, out_file= dot_data, 
                          feature_names= data1_2.columns[:-1],
                          class_names  = ['0','1','2'],
                          filled=True,rounded=True,
                          special_characters=True,
                      label='all',impurity=True,proportion=True,
                      
                    )  
graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
Image(graph.create_png())

predict3 = tree3.predict(data1_2.iloc[:,:-1].iloc[[s for s in range(len(data1_2)) if s not in idx3]])
ytrue3 = pd.Series(data1_2['lable'].iloc[[s for s in range(len(data1_2)) if s not in idx3]])
pd.crosstab(ytrue3, predict3, rownames=['Actual'], colnames=['Predicted'], margins = True)