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
import scipy.cluster.hierarchy as shc 
from sklearn.cluster import AgglomerativeClustering

def clust_kmean(k,data):
    kmeans = KMeans(n_clusters=k, max_iter=300, n_init=10, random_state=0)
    kmeans.fit(data)
    data['lable'] = kmeans.labels_
    return(data)

def clust_hier(k, data):
    plt.title("Dendrograms") 
    shc.dendrogram(shc.linkage(data, method='ward'))
    cluster = AgglomerativeClustering(n_clusters = k, affinity='euclidean', linkage='ward') 
    lable = cluster.fit_predict(data)
    data['lable'] = lable
    return(data)


#draw cluster wordcloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

def draw_worcloud(data):
    clust = list(Counter(data['lable']))
    for i in clust:
        cluster_doc = tf_dataframe.loc[tf_dataframe['lable']==i]
        count = list(cluster_doc.sum())  
        count_dict = {w:v for w,v in zip(word,count)}    
        wordcloud = WordCloud(background_color='white').fit_words(count_dict)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

data1 = clust_kmean(2,tf_dataframe)
draw_worcloud(data1)




data2 = clust_hier(2, tf_dataframe)
draw_worcloud(data2)

from sklearn import metrics
import numpy as np

score1 = metrics.silhouette_score(tf_dataframe, data1['lable'])

data1_2 = clust_kmean(3,tf_dataframe)
score1_2 = metrics.silhouette_score(tf_dataframe, data1_2['lable'])

data1_3 = clust_kmean(4,tf_dataframe)
score1_3 = metrics.silhouette_score(tf_dataframe, data1_3['lable'])

score_list = []
for i in range(2,60):
    data = clust_kmean(i, tf_dataframe)
    score = metrics.silhouette_score(tf_dataframe, data['lable'])
    score_list.append(score)
    
fig = plt.figure()
ax = fig.add_subplot()

ax.set_xlabel('number of k')
ax.set_ylabel('score')

x = np.array([i for i in range(2,60)])
y = np.array(score_list)


ax.scatter(x,y, s=4, cmap="RdBu")

plt.show()   