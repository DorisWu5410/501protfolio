#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 23:21:30 2021

@author: jiahuiwu
"""
import pymysql
import pandas as pd
from generate_tablelist import clust_table
from map import generateBasemap
import folium
import matplotlib.colors as mcolors
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import sklearn.cluster

conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')




#__________________________________________________________________________
#clustering with Pickup locations


def get_inputMatrix(year, month):
    time = year + '_' + month
    df = pd.DataFrame()
    
    for tname in clust_table:
        if time in tname:
            cur = conn.cursor()
            query = "select record_id, trip_distance, PU_lat, PU_long, DO_lat, DO_long, time, PU_timepoint from " + tname + ";"
            cur.execute(query)
            result = cur.fetchall()
    
            if 'yellow' in tname:
                lable = 'yellow'
            elif 'green' in tname:
                lable = 'green'
            else: 
                lable = 'fhv'
        
            feature = ['record_id', 'trip_distance', 'PU_lat', 'PU_long', 'DO_lat', 'DO_long', 'time', 'PU_timepoint','car_type']
            df_dict = dict(zip(feature,[[] for i in range(0,len(feature))]))
    
            #discard record with none value of the aboved feature
            # select subset of data for clustering
            for s in result:
                k = np.random.uniform(low=0.0, high=1.0)
                if k < 0.3:
                    if None not in s and 'nan' not in s:
                        for i in range(0,len(feature)-1):
                            df_dict[feature[i]].append(s[i])
                        df_dict['car_type'].append(lable)    
                
            matrix = pd.DataFrame(df_dict)
            df = pd.concat([df, matrix], axis=0)
    return(df)

get_inputMatrix('2016', '06').to_csv('2016_06.csv')
get_inputMatrix('2018', '04').to_csv('2018_04.csv')
get_inputMatrix('2020', '08').to_csv('2020_08.csv')



from sklearn.cluster import KMeans    
from sklearn.preprocessing import normalize


def clust_kmeans(year,month,feature_list,k,df):
   kmeans = KMeans(n_clusters = k, max_iter=300, n_init=20, random_state=0)
   input_data = df[feature_list]
   
   scaled_data = normalize(input_data)   
   kmeans.fit(scaled_data)
   
   df['clust'] = kmeans.labels_        
   return(df)


#hiera

import scipy.cluster.hierarchy as shc 
from sklearn.cluster import AgglomerativeClustering


def clust_hiera(year, month,feature_list,k,df):
    input_data = df[feature_list]
    
    data_scaled = normalize(input_data)
    plt.title("Dendrograms") 
    shc.dendrogram(shc.linkage(data_scaled, method='ward'))
    
    cluster = AgglomerativeClustering(n_clusters = k, affinity='euclidean', linkage='ward') 
    lable = cluster.fit_predict(data_scaled)
    df['clust'] = lable
    
    return(df)
   
def clust_DBSCAN(year,month,feature_list,df):
    dbscan = sklearn.cluster.DBSCAN(eps=0.00003, min_samples=4)
    input_data = df[feature_list]
    data_scaled = normalize(input_data)
    dbscan.fit(data_scaled)
    df['clust'] = dbscan.labels_        
    return(df)

# df = clust_kmeans('2018','04',['PU_lat', 'PU_long'],3)

def count_PUlatlong(df):
    PU_latlong_list = []
    for _ ,r in df.iterrows():
        PU_latlong_list.append((r['PU_lat'],r['PU_long']))
    return(Counter(PU_latlong_list))


def add_point_to_map(df):
    map1 = generateBasemap()
    col_list = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.BASE_COLORS.keys())
    count_dict = count_PUlatlong(df)
    
    for i in range(0,df.count()[0]):
        lat = float(df['PU_lat'].iloc[i])
        long = float(df['PU_long'].iloc[i])
        loc = (str(lat),str(long))
        color = col_list[df['clust'].iloc[i]]
        folium.CircleMarker(location=[lat,long],fill=True,
                            radius = count_dict[loc]/100+2,color = color).add_to(map1)
    return(map1)


def kmeans_loc(year, month, feature_list,k,inputdata):
    df = clust_kmeans(year,month,feature_list,k,inputdata)
    map1 = add_point_to_map(df)
    map1.save("clustMap_kmeans"+year+'_'+ month +'k='+ str(k) + ".html")

def hiera_loc(year, month, feature_list,k,inputdata):
    df = clust_hiera(year, month, feature_list, k,inputdata)
    map1 = add_point_to_map(df)
    map1.save("clustMap_hiera"+year+'_'+ month +'k='+ str(k) + ".html")
    
def DBSCAN_loc(year, month, feature_list,inputdata):
    df = clust_DBSCAN(year, month, feature_list,inputdata)
    map1 = add_point_to_map(df)
    map1.save("clustMap_DBSCAN"+year+'_'+ month + ".html")

# def map_before_clust(year, month, feature_list):
#     df = clust_kmeans(year,month,feature_list,3)
#     map1 = generateBasemap()
#     count_dict = count_PUlatlong(df)
    
#     for i in range(0,df.count()[0]):
#         lat = float(df['PU_lat'].iloc[i])
#         long = float(df['PU_long'].iloc[i])
#         loc = (str(lat),str(long))
#         folium.CircleMarker(location=[lat,long],fill=True, color = 'grey',
#                             radius = count_dict[loc]/330+2).add_to(map1)
#     map1.save("brforeClustMap"+year+'_'+ month + ".html")




# cluster based on pick-up location
df1 = get_inputMatrix('2018', '04')
kmeans_loc('2018', '04', ['PU_lat', 'PU_long'], 5, df1)
hiera_loc('2018', '04', ['PU_lat', 'PU_long'], 5, df1)
DBSCAN_loc('2018', '04', ['PU_lat', 'PU_long'], df1)

df2 = get_inputMatrix('2016', '06')
kmeans_loc('2016', '06', ['PU_lat', 'PU_long'], 3, df2)
hiera_loc('2016', '06', ['PU_lat', 'PU_long'],3, df2)
DBSCAN_loc('2016', '06', ['PU_lat', 'PU_long'], df2)

df3 = get_inputMatrix('2020', '08')
kmeans_loc('2020', '08', ['PU_lat', 'PU_long'], 7, df3)
hiera_loc('2020', '08', ['PU_lat', 'PU_long'],7, df3)
DBSCAN_loc('2020', '08', ['PU_lat', 'PU_long'], df3)
  
  


#silhouette_score

from sklearn import metrics
df = get_inputMatrix('2018', '04')

score_list = []
for i in range(2,10):
    data = clust_kmeans('2018', '04', ['PU_lat', 'PU_long'], i,df)
    score = metrics.silhouette_score(data[['PU_lat', 'PU_long']], data['clust'])
    score_list.append(score)
    
fig = plt.figure()
ax = fig.add_subplot()

ax.set_xlabel('number of k')
ax.set_ylabel('score')

x = np.array([i for i in range(2,10)])
y = np.array(score_list)


ax.scatter(x,y, s=4, cmap="RdBu")

plt.show()   


# k = 3 is better for kmeans


  






#________________________________________________________________



#cluster with PU location and time 



  
# col_list = list(mcolors.TABLEAU_COLORS.values()) 
# color_for_each = [col_list[i] for i in list(df['clust'])] 
# fig = plt.figure()
# ax = fig.add_subplot(111,projection='3d')

# ax.set_zlim(0, 24)
# ax.set_xlabel('pickup latitude')
# ax.set_ylabel('pickup longitude')
# ax.set_zlabel('pickup time point')
# x = np.array([float(s) for s in list(df['PU_lat'])])

# y = np.array([float(s) for s in list(df['PU_long'])])

# z = np.array([float(s) for s in list(df['PU_timepoint'])])

# ax.scatter(x,y,z, c = color_for_each, s=0.5, cmap="RdBu")

# plt.show()   
import plotly.express as px 



def plot_loc_time(year,month,k,df):
    df = clust_kmeans(year,month,['PU_lat', 'PU_long', 'PU_timepoint'],k, df)
    x = [float(s) for s in list(df['PU_lat'])]
    y = [float(s) for s in list(df['PU_long'])]
    z = [float(s) for s in list(df['PU_timepoint'])]
    
    count_dict = count_PUlatlong(df)
    count_list = []
    lat_list = list(df['PU_lat'])
    long_list = list(df['PU_long'])
    for i in range(0,len(df['PU_lat'])):
        loc = (lat_list[i],long_list[i])
        count = count_dict[loc]
        count_list.append(count)
        
    plot_df = pd.DataFrame({'PU_lat': x,'PU_long':y, 'PU_timepoint':z, 'clust':[str(c) for c in list(df['clust'])],'count' : count_list})  
    
    fig = px.scatter_3d(plot_df, x='PU_lat', y='PU_long', z='PU_timepoint',
                  color='clust', size = 'count',size_max=20)
    
    fig.update_layout(scene = dict(
                        xaxis_title='pickup latitude',
                        yaxis_title='pickup longitude',
                        zaxis_title='pickup time point'))
    
    fig.update_traces(marker=dict(line=dict(width=0)))
    return(fig)
    # fig.write_html("3d_clust"+year + '_' + month + ".html")
                      
df = get_inputMatrix('2019', '07')
plot_loc_time('2019', '07', 3,df).write_html('3d_clust2019_07.html')

df = get_inputMatrix('2018', '05')
plot_loc_time('2018', '05', 5).write_html('3d_clust2018_05.html')

df = get_inputMatrix('2019', '07')
plot_loc_time('2020', '09', 7).write_html('3d_clust2020_09.html')









#____________________________________________________

#distance metric








from sklearn.neighbors import DistanceMetric

latlist = get_inputMatrix('green_tripdata2020_05')['PU_lat']
longlist = get_inputMatrix('green_tripdata2020_05')['PU_long']

scale_lat = np.array([float(s) for s in list(latlist)])
mean_x = np.mean(scale_lat)
sd_x = np.var(scale_lat)**0.5
scale_lat = [(s-mean_x)/sd_x for s in scale_lat]

scale_long = np.array([float(s) for s in list(longlist)])
mean_x = np.mean(scale_long)
sd_x = np.var(scale_long)**0.5
scale_long = [(s-mean_x)/sd_x for s in scale_long]

location_list = [] 
for i in range(0,len(latlist)):
    loc = [scale_lat[i],scale_long[i]]
    location_list.append(loc)
    
x = []
for i in range(1,len(location_list)+1):
    part = [i for j in range(len(location_list))]
    x = x + part
    
y = []
for i in range(len(location_list)):
    part = [i for i in range(1,len(location_list)+1)]
    y = y + part

def distance_plot(dist_type):
    dist = DistanceMetric.get_metric(dist_type)
    dist_matrix = dist.pairwise(location_list)
    
    dist_list = []
    for i in range(0,len(location_list)):
        for j in range(0,len(location_list)):
            dist_list.append(dist_matrix[i,j])
    
    plot_df = pd.DataFrame({'data1': x,'data2':y, 'distance':dist_list})  
        
    fig = px.scatter_3d(plot_df, x='data1', y='data2', z='distance',color='distance')
    
    fig.update_layout(scene = dict(
                        xaxis_title='data point id',
                        yaxis_title='data point id',
                        zaxis_title='pairwise distance'))
    fig.update_traces(marker=dict(size = 3, line=dict(width=0)))
    fig.write_html(dist_type +'.html')
    
distance_plot('manhattan')
distance_plot('euclidean')



# import plotly.graph_objects as go

# dist = DistanceMetric.get_metric('euclidean')
# dist_matrix = dist.pairwise(location_list)
# fig = go.Figure(data=[go.Surface(z=dist_matrix)])
# fig.update_layout(scene = dict(
#                         zaxis_title='euclidean distance'))
# fig.write_html('euclidean.html')


# dist = DistanceMetric.get_metric('manhattan')
# dist_matrix = dist.pairwise(location_list)
# fig = go.Figure(data=[go.Surface(z=dist_matrix)])
# fig.update_layout(scene = dict(
#                         zaxis_title='manhattan distance'))
# fig.write_html('manhattan.html')


from numpy import dot
from numpy.linalg import norm

array = []
for i in range(len(location_list)):
    row = []
    for j in range(len(location_list)):
        cos_sim = dot(location_list[i], location_list[j])/(norm(location_list[i])*norm(location_list[j]))
        row.append(cos_sim)
    array.append(row)
dist_matrix = np.array(array)

# fig = go.Figure(data=[go.Surface(z=dist_matrix)])
# fig.update_layout(scene = dict(
#                         zaxis_title='cos_sim similarity'))
# fig.write_html('cos_sim.html')

dist_list = []
for i in range(0,len(location_list)):
    for j in range(0,len(location_list)):
        dist_list.append(dist_matrix[i,j])

plot_df = pd.DataFrame({'data1': x,'data2':y, 'distance':dist_list})  
    
fig = px.scatter_3d(plot_df, x='data1', y='data2', z='distance',color='distance')

fig.update_layout(scene = dict(
                    xaxis_title='data point id',
                    yaxis_title='data point id',
                    zaxis_title='pairwise distance'))
fig.update_traces(marker=dict(size = 3, line=dict(width=0)))
fig.write_html('cos_sim.html')


