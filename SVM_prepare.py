#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 14:46:39 2021

@author: jiahuiwu
"""

#predicting PU density for an average day of week and time of a day
import pymysql
import numpy as np
from collections import Counter
import pandas as pd
import random
from generate_tablelist import clust_table;
from datetime import datetime as dt
import csv
from map import zone_ID_col
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree
import matplotlib.pyplot as plt
import seaborn as sns


import pydotplus
import graphviz
from IPython.display import Image  
import pydotplus
from six import StringIO
import os
from random import sample
from sklearn import svm
from sklearn.naive_bayes import GaussianNB

conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')


#weather data
import datetime as dt
weather = pd.read_csv('/Users/jiahuiwu/Desktop/501/portfolio/weather2018_1-8.csv') 

def convert_date_weather(date_weather):
    return(dt.datetime.strptime(date_weather, '%m/%d/%Y %H:%M:%S'))

def convert_date_car(date, timepoint):
    time = date + ' ' + str(timepoint)
    return(dt.datetime.strptime(time, '%Y-%m-%d %H'))

weather['Datetime_adj'] = [convert_date_weather(s) for s in list(weather['Date time'])] 

temp_dict = {}
for _,r in weather.iterrows():
    temp_dict[r['Datetime_adj']] = r['Temperature']
    
prec_dict = {} 
for _,r in weather.iterrows():
    prec_dict[r['Datetime_adj']] = r['Precipitation']
       
snow_dict = {} 
for _,r in weather.iterrows():
    snow_dict[r['Datetime_adj']] = r['Snow Depth']
    
wind_dict = {} 
for _,r in weather.iterrows():
    wind_dict[r['Datetime_adj']] = r['Wind Speed']
    


# get records count based on Pickup_datetime, PU_lat, PU_long, PU_timepoint, day_of_week
def count_DTPU(year_month_list):
    cur = conn.cursor()
    date_PU_day=[]
    for date in year_month_list:
        for tname in clust_table: 
            if date in tname:
                query = "select Pickup_datetime, PU_lat, PU_long, PU_timepoint, day_of_week from " + tname + " where PU_lat is not null;"
                cur.execute(query)
                result = cur.fetchall()
                date_PU_day = date_PU_day + [(s[0].replace(' ','',1)[:10], s[1], s[2], int(float(s[3])),s[4])for s in result]
            
    count_dict = Counter(date_PU_day)
    df_dict = {}
    key = list(count_dict.keys())
    count = list(count_dict.values())
    for i in range(len(count)):
        if count[i]>=13:
            count[i] =13
    
    df_dict['PU_lat'] = [s[1] for s in key]
    df_dict['PU_long'] = [s[2] for s in key]
    df_dict['timepoint'] = [s[3] for s in key]
    df_dict['dayofweek'] = [s[4] for s in key]
    df_dict['count'] = count
    
    df_dict['temp'] = [temp_dict.get(convert_date_car(s[0],s[3]), None) for s in key]         
    df_dict['Precipitation'] = [prec_dict.get(convert_date_car(s[0],s[3]), None) for s in key]
    df_dict['snow'] = [snow_dict.get(convert_date_car(s[0],s[3]), None) for s in key]
    df_dict['wind'] = [wind_dict.get(convert_date_car(s[0],s[3]), None) for s in key]
    
    return(pd.DataFrame(df_dict))
   
         
train = count_DTPU(['2018_07','2018_06'])
one = train[train['count'] == 1].index.tolist()
two = train[train['count'] == 2].index.tolist()
remove_idx = random.sample(one,int(len(one)//4)) 
train = train.drop(train.index[remove_idx])
train = train[train['temp'].notna()]
# train = train[train['snow'].notna()]

supp = count_DTPU(['2018_04','2018_05','2018_06','2018_03','2018_01','2018_02'])
supp = supp[supp['temp'].notna()]
# supp = supp[supp['snow'].notna()]
supp1 = supp[supp['count'] >= 6]
train = pd.concat([train,supp1,supp1,supp1,supp1,supp1])

train.to_csv('DT_train.csv')

test = count_DTPU(['2018_08'])
# test_part1 = test.iloc[random.sample(range(1,len(test)),int(len(test)//5)) ]
test.to_csv('DT_test.csv')


def class_divide(x):
    if x==1: return('low')
    elif 2<=x and x<5: return('medium')
    else: return('high')

train['label'] = list(map(class_divide, train['count']))





test['label'] = list(map(class_divide, test['count']))
test = test[test['temp'].notna()]



Naive = GaussianNB()
Naive.fit(train.iloc[:,[0,1,2,3,5,6]], train['label'])

pd.crosstab(test['label'], pd.Series(Naive.predict(test.iloc[:,[0,1,2,3,5,6]])), rownames=['Actual'], colnames=['Predicted'], margins = True)





#SVM
random.seed(10)
idx1 = random.sample(range(1,len(train)),int(len(train)//10)) 

SVM1 = svm.SVC(C=1.0, max_iter=20000)
SVM1.fit(train.iloc[idx1,[0,1,2,3,5,6]], train['label'].iloc[idx1])
pd.crosstab(test['label'], pd.Series(SVM1.predict(test.iloc[:,[0,1,2,3,5,6]])), rownames=['Actual'], colnames=['Predicted'], margins = True)


SVM2 = svm.SVC(C = 1, kernel='poly', degree=3, gamma='auto')
SVM2.fit(train.iloc[idx1,[0,1,2,3,5,6]], train['label'].iloc[idx1])
pd.crosstab(test['label'], pd.Series(SVM2.predict(test.iloc[:,[0,1,2,3,5,6]])), rownames=['Actual'], colnames=['Predicted'], margins = True)





