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


conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')

# add day_of week to each record
def add_dayofweek(tname):
    cur = conn.cursor()
    query = "select Pickup_datetime, record_id from " + tname
    cur.execute(query)
    result = cur.fetchall()
    date = [s[0] for s in result]
    ID = [s[1] for s in result]
    
    query = "alter table " + tname +  " add column day_of_week varchar(30);"
    cur.execute(query)
    
    for i in range(len(date)):
        if date[i][0]==' ':
            date[i] = date[i].replace(' ','',1)
        DoW = dt.fromisoformat(date[i]).weekday()
        query = "update " + tname + " set day_of_week = " + '"'+ str(DoW) + '"'  + " where record_id = " + str(ID[i]) + ";"
        cur.execute(query)
    print(tname)

# for tname in clust_table:
#     add_dayofweek(tname)



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
                date_PU_day = date_PU_day + [(s[0].replace(' ','',1)[:10], s[1], s[2], int(float(s[3])), s[4]) for s in result]
            
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
            
    return(pd.DataFrame(df_dict))
   
         
train = count_DTPU(['2018_07'])
# one = train[train['count'] == 1].index.tolist()
# two = train[train['count'] == 2].index.tolist()
# remove_idx = sample(one,int(len(one)//3)) + sample(two, len(two)//4)
# train = train.drop(train.index[remove_idx])


supp = count_DTPU(['2018_04','2018_05','2018_06','2018_03','2018_01','2018_02'])
supp1 = supp[supp['count'] >= 6]
supp2 = supp[supp['count'] >= 8]

train = pd.concat([train,supp1,
                  supp2,
                  ])

train.to_csv('DT_train.csv')

test = count_DTPU(['2018_08'])
# test_part1 = test.iloc[random.sample(range(1,len(test)),int(len(test)//5)) ]
test.to_csv('DT_test.csv')


#tree
random.seed(10)
idx1 = random.sample(range(1,len(train)),int(len(train)//1.2)) 

random.seed(20)
idx2 = random.sample(range(1,len(train)),int(len(train)//1.2)) 

random.seed(30)
idx3 = random.sample(range(1,len(train)),int(len(train)//1.2)) 
    
random.seed(40)
idx4 = random.sample(range(1,len(train)),int(len(train)//1.2)) 

def find_alpha(idx):
    mse_list = []
    temp_test = [i for i in range(len(train)) if i not in idx]
    for alpha in np.arange(0.00001, 0.0003, 0.00001):
        newtree = DecisionTreeRegressor(ccp_alpha = alpha)
        newtree.fit(train[['PU_lat','PU_long','timepoint','dayofweek']].iloc[idx], train['count'].iloc[idx])
        predict = newtree.predict(train[['PU_lat','PU_long','timepoint','dayofweek']].iloc[temp_test])
        mse = sum((np.array(predict) - np.array(train['count'].iloc[temp_test]))**2)/len(predict)
        mse_list.append(mse)
    alpha = list(np.arange(0.00001, 0.0003, 0.00001))[mse_list.index(min(mse_list))]
    return(alpha)

find_alpha(idx1)



#fit tree

def fit_tree(idx):
    alpha = 0.00029
    newtree = DecisionTreeRegressor(ccp_alpha = alpha)
    newtree.fit(train[['PU_lat','PU_long','timepoint','dayofweek']].iloc[idx], train['count'].iloc[idx])
    # fig=plt.figure(figsize=(380,375))
    # tree.plot_tree(newtree,
    #                 feature_names=train.columns[:4], 
    #                 filled=True)
    # fig.savefig(figname + ".png")
    return(newtree)




    

tree1 = fit_tree(idx1)
# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
# dot_data = StringIO()    
# tree.export_graphviz(tree1, out_file= dot_data, 
#                           feature_names=train.columns[:4],
#                           class_names=train.columns[4],
#                           filled=True,rounded=True,
#                           special_characters=False,
#                       label='all',impurity=False,proportion=True
#                     )  
# graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
# Image(graph.create_png())




tree2 = fit_tree(idx2)
# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
# dot_data = StringIO()  
# tree.export_graphviz(tree2, out_file= dot_data, 
#                           feature_names=train.columns[:4],
#                           class_names=train.columns[4],
#                           filled=True,rounded=True,
#                           special_characters=False,
#                       label='all',impurity=False,proportion=True
#                     )  
# graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
# Image(graph.create_png())




tree3 = fit_tree(idx3)
# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
# dot_data = StringIO()  
# tree.export_graphviz(tree3, out_file= dot_data, 
#                           feature_names=train.columns[:4],
#                           class_names=train.columns[4],
#                           filled=True,rounded=True,
#                           special_characters=False,
#                       label='all',impurity=False,proportion=True
#                     )  
# graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
# Image(graph.create_png())




tree4 = fit_tree(idx4)
# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
# dot_data = StringIO()  
# tree.export_graphviz(tree4, out_file= dot_data, 
#                           feature_names=train.columns[:4],
#                           class_names=train.columns[4],
#                           filled=True,rounded=True,
#                           special_characters=False,
#                       label='all',impurity=False,proportion=True
#                     )  
# graph = pydotplus.graph_from_dot_data(dot_data.getvalue().replace('value','components'))
# Image(graph.create_png())



#average
def count_avg(dataframe):
    dict_ = {}

    for _, row in dataframe.iterrows():
        loc_time_dow = ((float(row['PU_lat']),float(row['PU_long'])), row['timepoint'], row['dayofweek'])
        if loc_time_dow in dict_:
            dict_[loc_time_dow].append(row['count'])
        else:
            dict_[loc_time_dow] = [row['count']]
    
    for i in dict_:
        dict_[i] = round(np.mean(dict_[i]),0)
    return(dict_)


def convert_to_df(dict_):
    average = pd.DataFrame()
    average['PU_lat'] = [s[0][0] for s in dict_.keys()]    
    average['PU_long'] = [s[0][1] for s in dict_.keys()]  
    average['timepoint'] = [s[1] for s in dict_.keys()]
    average['dayofweek'] = [s[2] for s in dict_.keys()]    
    average['avg_count'] = [s for s in dict_.values()]
    return(average)


test_dict = count_avg(test)
test_avg = convert_to_df(test_dict)

predict1 = tree1.predict(test_avg[['PU_lat','PU_long','timepoint','dayofweek']])
predict2 = tree2.predict(test_avg[['PU_lat','PU_long','timepoint','dayofweek']])
predict3 = tree3.predict(test_avg[['PU_lat','PU_long','timepoint','dayofweek']])
predict4 = tree4.predict(test_avg[['PU_lat','PU_long','timepoint','dayofweek']])


predict_final = (np.array(predict1) + np.array(predict2) + np.array(predict3) + np.array(predict4))/4

def compute_mse(pred,true):
    return(sum((np.array(pred)-np.array(true))**2)/len(pred))


compute_mse(predict_final, test_avg['avg_count'])
plot_df = sns.boxplot(x = test_avg['avg_count'], y = predict_final)
plot_df.set(ylabel = 'predicted', xlabel = 'true')
plot_df.set_ylim([0,10])






#random forest
from sklearn.ensemble import RandomForestRegressor

# Instantiate model with 1000 decision trees
rf = RandomForestRegressor(n_estimators = 100, random_state = 40, max_features =2, ccp_alpha=0.0006)
# Train the model on training data
rf.fit(train[['PU_lat','PU_long','timepoint','dayofweek']], train['count'])

predict_rf = rf.predict(test_avg[['PU_lat','PU_long','timepoint','dayofweek']])

compute_mse(predict_rf, test_avg['avg_count'])
plot_rf = sns.boxplot(x = test_avg['avg_count'], y = predict_rf)
plot_rf.set(ylabel = 'predicted', xlabel = 'true')
plot_rf.set_ylim([0,10])



# 

predict_dict = {}
predict_dict_rf = {}

for i in range(len(test_dict)):
    predict_dict[list(test_dict.keys())[i]]=predict_final[i]
    predict_dict_rf[list(test_dict.keys())[i]] = predict_rf[i]





# confusion matrix

ytrue = pd.Series(test_dict.values())
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict1]), rownames=['Actual'], colnames=['Predicted'], margins = True)
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict2]), rownames=['Actual'], colnames=['Predicted'], margins = True)    
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict3]), rownames=['Actual'], colnames=['Predicted'], margins = True)    
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict4]), rownames=['Actual'], colnames=['Predicted'], margins = True)    
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict_final]), rownames=['Actual'], colnames=['Predicted'], margins = True)    
pd.crosstab(ytrue, pd.Series([round(s,0) for s in predict_rf]), rownames=['Actual'], colnames=['Predicted'], margins = True)
